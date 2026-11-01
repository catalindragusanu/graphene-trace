import React, { useState } from 'react';
import { useAlerts } from '../../hooks/useAlerts';
import { AlertSeverity } from '../../types/alert';
import '../../styles/AlertsList.css';

interface AlertsListProps {
  onAlertClick?: (frameId: number) => void;
}

export const AlertsList: React.FC<AlertsListProps> = ({ onAlertClick }) => {
  const [severityFilter, setSeverityFilter] = useState<AlertSeverity | 'all'>('all');
  const [showAcknowledged, setShowAcknowledged] = useState(false);

  const { data: alerts, isLoading, error } = useAlerts({
    severity: severityFilter !== 'all' ? severityFilter : undefined,
  });

  if (isLoading) {
    return <div className="alerts-list loading">Loading alerts...</div>;
  }

  if (error) {
    return <div className="alerts-list error">Failed to load alerts</div>;
  }

  const filteredAlerts = alerts?.filter(alert =>
    showAcknowledged ? true : !alert.acknowledged
  ) || [];

  const getSeverityBadgeClass = (severity: AlertSeverity): string => {
    switch (severity) {
      case 'high':
        return 'severity-high';
      case 'medium':
        return 'severity-medium';
      case 'low':
        return 'severity-low';
      default:
        return '';
    }
  };

  return (
    <div className="alerts-list">
      <div className="alerts-header">
        <h2>Pressure Alerts</h2>
        <div className="alerts-count">
          {filteredAlerts.length} {filteredAlerts.length === 1 ? 'alert' : 'alerts'}
        </div>
      </div>

      <div className="alerts-filters">
        <div className="filter-group">
          <label htmlFor="severity-filter">Severity:</label>
          <select
            id="severity-filter"
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value as AlertSeverity | 'all')}
          >
            <option value="all">All</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>

        <div className="filter-checkbox">
          <input
            type="checkbox"
            id="show-acknowledged"
            checked={showAcknowledged}
            onChange={(e) => setShowAcknowledged(e.target.checked)}
          />
          <label htmlFor="show-acknowledged">Show acknowledged</label>
        </div>
      </div>

      {filteredAlerts.length === 0 ? (
        <div className="no-alerts">
          <p>No alerts found</p>
        </div>
      ) : (
        <div className="alerts-container">
          {filteredAlerts.map(alert => (
            <div
              key={alert.id}
              className={`alert-card ${getSeverityBadgeClass(alert.severity)} ${alert.acknowledged ? 'acknowledged' : ''}`}
              onClick={() => onAlertClick && onAlertClick(alert.frame_id)}
            >
              <div className="alert-header-row">
                <span className={`severity-badge ${getSeverityBadgeClass(alert.severity)}`}>
                  {alert.severity.toUpperCase()}
                </span>
                {alert.acknowledged && (
                  <span className="acknowledged-badge">✓ Acknowledged</span>
                )}
              </div>

              <div className="alert-time">
                {new Date(alert.created_at).toLocaleString()}
              </div>

              <div className="alert-details">
                <div className="detail-item">
                  <span className="detail-label">Region:</span>
                  <span className="detail-value">
                    {alert.region
                      ? `(${alert.region.x1}, ${alert.region.y1}) to (${alert.region.x2}, ${alert.region.y2})`
                      : 'Unavailable'}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Area:</span>
                  <span className="detail-value">{alert.region ? `${alert.region.area} pixels` : 'Unavailable'}</span>
                </div>
              </div>

              {alert.acknowledged && alert.acknowledged_at && (
                <div className="acknowledged-info">
                  Acknowledged {new Date(alert.acknowledged_at).toLocaleString()}
                </div>
              )}

              <div className="alert-action">
                Click to view frame
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
