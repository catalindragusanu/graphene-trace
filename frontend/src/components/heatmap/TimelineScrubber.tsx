import React from 'react';
import { FrameSummary } from '../../types/frame';
import '../../styles/Timeline.css';

interface TimelineScrubberProps {
  frames: FrameSummary[];
  currentIndex: number;
  onIndexChange: (index: number) => void;
}

export const TimelineScrubber: React.FC<TimelineScrubberProps> = ({
  frames,
  currentIndex,
  onIndexChange
}) => {
  if (frames.length === 0) {
    return <div className="timeline-empty">No frames available</div>;
  }

  const currentFrame = frames[currentIndex];

  const handlePrevious = () => {
    if (currentIndex > 0) {
      onIndexChange(currentIndex - 1);
    }
  };

  const handleNext = () => {
    if (currentIndex < frames.length - 1) {
      onIndexChange(currentIndex + 1);
    }
  };

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onIndexChange(parseInt(e.target.value));
  };

  return (
    <div className="timeline-scrubber">
      <div className="timeline-controls">
        <button
          onClick={handlePrevious}
          disabled={currentIndex === 0}
          className="timeline-button"
        >
          &#9664; Previous
        </button>

        <div className="timeline-info">
          <div className="frame-number">
            Frame {currentIndex + 1} of {frames.length}
          </div>
          <div className="frame-time">
            {new Date(currentFrame.captured_at).toLocaleString()}
          </div>
          <div className="frame-status">
            {currentFrame.has_alerts && (
              <span className="alert-badge">⚠ Alert</span>
            )}
            {currentFrame.has_metrics && (
              <span className="metrics-badge">📊 Metrics</span>
            )}
          </div>
        </div>

        <button
          onClick={handleNext}
          disabled={currentIndex === frames.length - 1}
          className="timeline-button"
        >
          Next &#9654;
        </button>
      </div>

      <div className="timeline-slider">
        <input
          type="range"
          min={0}
          max={frames.length - 1}
          value={currentIndex}
          onChange={handleSliderChange}
          className="slider"
        />
      </div>
    </div>
  );
};
