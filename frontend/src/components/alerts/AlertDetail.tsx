import React from 'react';
import { Alert } from '../../types/alert';
import { useAcknowledgeAlert } from '../../hooks/useAlerts';
import '../../styles/AlertDetail.css';

interface AlertDetailProps {
  alert: Alert;
  onClose?: () => void;
}

export const AlertDetail: React.FC<AlertDetailProps> = ({ alert, onClose }) => {
  const acknowledgeMutation = useAcknowledgeAlert();

  const handleAcknowledge = async () => {
    try {
      await acknowledgeMutation.mutateAsync(alert.id);
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
  };

  const getSeverityColor = (severity: string): string => {
    switch (severity) {
      case 'high':
        return '#dc2626';
      case 'medium':
        return '#f59e0b';
      case 'low':
        return '#fbbf24';
      default:
        return '#6b7280';
    }
  };

  return (
    <div className="alert-detail-modal">
      <div className="alert-detail-content">
        <div className="alert-detail-header">
          <h2>Alert Details</h2>
          {onClose && (
            <button className="close-btn" onClick={onClose}>
              ✕
            </button>
          )}
        </div>

        <div className="alert-detail-body">
          <div className="severity-section">
            <div className="severity-label">Severity</div>
            <div
              className="severity-value"
              style={{ backgroundColor: getSeverityColor(alert.severity), color: 'white' }}
            >
              {alert.severity.toUpperCase()}
            </div>
          </div>

          <div className="detail-section">
            <div className="detail-row">
              <span className="label">Created:</span>
              <span className="value">{new Date(alert.created_at).toLocaleString()}</span>
            </div>

            <div className="detail-row">
              <span className="label">Frame ID:</span>
              <span className="value">#{alert.frame_id}</span>
            </div>

            <div className="detail-row">
              <span className="label">Status:</span>
              <span className="value">
                {alert.acknowledged ? (
                  <span className="status-acknowledged">✓ Acknowledged</span>
                ) : (
                  <span className="status-pending">Pending</span>
                )}
              </span>
            </div>
          </div>

          <div className="region-section">
            <h3>High Pressure Region</h3>
            {alert.region ? <div className="region-grid">
              <div className="region-item">
                <span className="region-label">Top-Left:</span>
                <span className="region-value">({alert.region.x1}, {alert.region.y1})</span>
              </div>
              <div className="region-item">
                <span className="region-label">Bottom-Right:</span>
                <span className="region-value">({alert.region.x2}, {alert.region.y2})</span>
              </div>
              <div className="region-item">
                <span className="region-label">Area:</span>
                <span className="region-value">{alert.region.area} pixels</span>
              </div>
            </div> : <p>Region unavailable</p>}
          </div>

          {alert.acknowledged && alert.acknowledged_at && (
            <div className="acknowledged-section">
              <div className="acknowledged-icon">✓</div>
              <div className="acknowledged-text">
                <div className="acknowledged-title">Acknowledged</div>
                <div className="acknowledged-time">
                  {new Date(alert.acknowledged_at).toLocaleString()}
                </div>
              </div>
            </div>
          )}

          {!alert.acknowledged && (
            <div className="actions-section">
              <button
                className="acknowledge-btn"
                onClick={handleAcknowledge}
                disabled={acknowledgeMutation.isPending}
              >
                {acknowledgeMutation.isPending ? 'Acknowledging...' : 'Acknowledge Alert'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
