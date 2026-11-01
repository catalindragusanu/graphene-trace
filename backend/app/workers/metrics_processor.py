"""Background worker for processing frame metrics"""
from sqlalchemy.orm import Session
from app.models.frame import Frame
from app.models.metric import Metric
from app.models.alert import Alert, AlertSeverity
from app.services.analytics_service import AnalyticsService
from app.utils.pressure_matrix import decode_matrix
from app.database import SessionLocal
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricsProcessor:
    """Worker for processing frame metrics in the background"""

    def __init__(self, db_session: Session = None):
        """
        Initialize metrics processor.

        Args:
            db_session: Database session (if None, will create new sessions)
        """
        self.analytics = AnalyticsService()
        self.db_session = db_session
        self.owns_session = db_session is None

    def _get_session(self) -> Session:
        """Get database session."""
        if self.db_session:
            return self.db_session
        return SessionLocal()

    def process_frame_metrics(self, frame_id: int, db: Session = None) -> bool:
        """
        Process metrics for a single frame.

        Args:
            frame_id: ID of the frame to process
            db: Database session (optional)

        Returns:
            bool: True if successful, False otherwise
        """
        if db is None:
            db = self._get_session()
            should_close = True
        else:
            should_close = False

        try:
            # Check if metrics already exist
            existing_metric = db.query(Metric).filter(Metric.frame_id == frame_id).first()
            if existing_metric:
                logger.debug(f"Metrics already exist for frame {frame_id}, skipping")
                return True

            # Get frame
            frame = db.query(Frame).filter(Frame.id == frame_id).first()
            if not frame:
                logger.warning(f"Frame {frame_id} not found")
                return False

            # Decode pressure matrix
            try:
                matrix = decode_matrix(frame.data)
            except Exception as e:
                logger.error(f"Error decoding frame {frame_id}: {e}")
                return False

            # Calculate metrics
            try:
                metrics_data = self.analytics.process_frame(matrix)
            except Exception as e:
                logger.error(f"Error calculating metrics for frame {frame_id}: {e}")
                return False

            # Create Metric record
            metric = Metric(
                frame_id=frame.id,
                peak_pressure=metrics_data["peak_pressure"],
                contact_area_percent=metrics_data["contact_area_percent"],
                high_pressure_region=metrics_data["high_pressure_region"],
                alert_generated=metrics_data["alert_generated"]
            )
            db.add(metric)

            # Create Alert if needed
            if metrics_data["alert_generated"]:
                # Map severity string to enum
                severity_map = {
                    "low": AlertSeverity.LOW,
                    "medium": AlertSeverity.MEDIUM,
                    "high": AlertSeverity.HIGH
                }
                severity = severity_map.get(
                    metrics_data["alert_severity"],
                    AlertSeverity.MEDIUM
                )

                alert = Alert(
                    frame_id=frame.id,
                    severity=severity,
                    region=metrics_data["high_pressure_region"],
                    acknowledged=False
                )
                db.add(alert)

            db.commit()
            logger.debug(f"Processed metrics for frame {frame_id}")
            return True

        except Exception as e:
            logger.error(f"Error processing frame {frame_id}: {e}")
            db.rollback()
            return False

        finally:
            if should_close:
                db.close()

    def process_unprocessed_frames(self, batch_size: int = 100, max_frames: int = None):
        """
        Process all frames that don't have metrics yet.

        Args:
            batch_size: Number of frames to process before committing (default: 100)
            max_frames: Maximum number of frames to process (None = all)

        Returns:
            int: Number of frames successfully processed
        """
        db = self._get_session()
        processed_count = 0
        error_count = 0

        try:
            # Find frames without metrics using LEFT JOIN
            query = db.query(Frame).outerjoin(Metric).filter(Metric.id.is_(None))

            if max_frames:
                query = query.limit(max_frames)

            unprocessed_frames = query.all()
            total_frames = len(unprocessed_frames)

            if total_frames == 0:
                logger.info("No unprocessed frames found")
                return 0

            logger.info(f"Processing {total_frames} unprocessed frames...")

            # Process frames in batches
            for i, frame in enumerate(unprocessed_frames, 1):
                success = self.process_frame_metrics(frame.id, db=db)

                if success:
                    processed_count += 1
                else:
                    error_count += 1

                # Progress update every 10%
                if i % max(1, total_frames // 10) == 0:
                    progress = (i / total_frames) * 100
                    logger.info(f"Progress: {i}/{total_frames} ({progress:.1f}%)")

            logger.info(f"Processing complete: {processed_count} successful, {error_count} errors")
            return processed_count

        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            raise

        finally:
            if self.owns_session:
                db.close()

    def reprocess_frame(self, frame_id: int) -> bool:
        """
        Reprocess metrics for a frame (deletes existing metrics first).

        Args:
            frame_id: ID of the frame to reprocess

        Returns:
            bool: True if successful
        """
        db = self._get_session()

        try:
            # Delete existing metrics
            db.query(Metric).filter(Metric.frame_id == frame_id).delete()

            # Delete existing alerts
            db.query(Alert).filter(Alert.frame_id == frame_id).delete()

            db.commit()

            # Process fresh metrics
            return self.process_frame_metrics(frame_id, db=db)

        except Exception as e:
            logger.error(f"Error reprocessing frame {frame_id}: {e}")
            db.rollback()
            return False

        finally:
            if self.owns_session:
                db.close()

    def get_processing_stats(self) -> dict:
        """
        Get statistics about frame processing.

        Returns:
            dict: Processing statistics
        """
        db = self._get_session()

        try:
            total_frames = db.query(Frame).count()
            processed_frames = db.query(Metric).count()
            total_alerts = db.query(Alert).count()

            unprocessed = total_frames - processed_frames
            completion_rate = (processed_frames / total_frames * 100) if total_frames > 0 else 0

            return {
                "total_frames": total_frames,
                "processed_frames": processed_frames,
                "unprocessed_frames": unprocessed,
                "completion_rate": completion_rate,
                "total_alerts": total_alerts
            }

        finally:
            if self.owns_session:
                db.close()


def main():
    """
    Main function for running the metrics processor as a standalone script.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Process frame metrics")
    parser.add_argument("--batch-size", type=int, default=100,
                        help="Batch size for processing (default: 100)")
    parser.add_argument("--max-frames", type=int, default=None,
                        help="Maximum frames to process (default: all)")
    parser.add_argument("--stats", action="store_true",
                        help="Show processing statistics only")

    args = parser.parse_args()

    processor = MetricsProcessor()

    if args.stats:
        stats = processor.get_processing_stats()
        print("\nProcessing Statistics:")
        print(f"  Total frames: {stats['total_frames']:,}")
        print(f"  Processed frames: {stats['processed_frames']:,}")
        print(f"  Unprocessed frames: {stats['unprocessed_frames']:,}")
        print(f"  Completion rate: {stats['completion_rate']:.1f}%")
        print(f"  Total alerts: {stats['total_alerts']:,}")
    else:
        print("=" * 60)
        print("Metrics Processor")
        print("=" * 60)
        print()

        processed = processor.process_unprocessed_frames(
            batch_size=args.batch_size,
            max_frames=args.max_frames
        )

        print()
        print(f"Processed {processed:,} frames")


if __name__ == "__main__":
    main()
