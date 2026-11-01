import React, { useState } from 'react';
import { useMetrics } from '../../hooks/useMetrics';
import { MetricsChart } from './MetricsChart';
import { PeriodSelector, TimePeriod } from './PeriodSelector';
import '../../styles/MetricsDashboard.css';

export const MetricsDashboard: React.FC = () => {
  const [period, setPeriod] = useState<TimePeriod>('24h');
  const [customRange, setCustomRange] = useState<{ start: Date; end: Date } | null>(null);

  const { data: metrics, isLoading, error } = useMetrics({
    start_time: customRange?.start.toISOString() || getStartTime(period),
    end_time: customRange?.end.toISOString() || new Date().toISOString(),
  });

  if (isLoading) {
    return <div className="metrics-dashboard loading">Loading metrics...</div>;
  }

  if (error) {
    return <div className="metrics-dashboard error">Failed to load metrics</div>;
  }

  if (!metrics || metrics.length === 0) {
    return <div className="metrics-dashboard empty">No metrics available</div>;
  }

  // Calculate summary statistics
  const avgPPI = metrics.reduce((sum, m) => sum + m.peak_pressure, 0) / metrics.length;
  const avgContactArea = metrics.reduce((sum, m) => sum + m.contact_area_percent, 0) / metrics.length;
  const alertCount = metrics.filter(m => m.alert_generated).length;
  const maxPPI = Math.max(...metrics.map(m => m.peak_pressure));

  return (
    <div className="metrics-dashboard">
      <div className="dashboard-header">
        <h2>Pressure Metrics Dashboard</h2>
        <PeriodSelector
          selectedPeriod={period}
          onPeriodChange={(newPeriod) => {
            setPeriod(newPeriod);
            setCustomRange(null);
          }}
          onCustomRangeChange={setCustomRange}
        />
      </div>

      <div className="summary-cards">
        <div className="summary-card">
          <div className="card-label">Average PPI</div>
          <div className="card-value">{avgPPI.toFixed(1)}</div>
          <div className="card-unit">mmHg</div>
        </div>

        <div className="summary-card">
          <div className="card-label">Max PPI</div>
          <div className="card-value">{maxPPI.toFixed(1)}</div>
          <div className="card-unit">mmHg</div>
        </div>

        <div className="summary-card">
          <div className="card-label">Avg Contact Area</div>
          <div className="card-value">{avgContactArea.toFixed(1)}%</div>
          <div className="card-unit">of sensor</div>
        </div>

        <div className="summary-card alert">
          <div className="card-label">Alert Count</div>
          <div className="card-value">{alertCount}</div>
          <div className="card-unit">high pressure events</div>
        </div>
      </div>

      <div className="charts-container">
        <div className="chart-wrapper">
          <h3>Peak Pressure Index Over Time</h3>
          <MetricsChart
            data={metrics}
            yKey="peak_pressure"
            title="PPI (mmHg)"
            color="rgb(255, 99, 132)"
            thresholdLine={{ value: 200, label: 'High Pressure Threshold' }}
          />
        </div>

        <div className="chart-wrapper">
          <h3>Contact Area Over Time</h3>
          <MetricsChart
            data={metrics}
            yKey="contact_area_percent"
            title="Contact Area (%)"
            color="rgb(54, 162, 235)"
          />
        </div>
      </div>

      <div className="metrics-table">
        <h3>Recent Metrics ({metrics.length} records)</h3>
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>PPI (mmHg)</th>
              <th>Contact Area (%)</th>
              <th>Alert</th>
              <th>Region</th>
            </tr>
          </thead>
          <tbody>
            {metrics.slice(0, 20).map((metric) => (
              <tr key={metric.id} className={metric.alert_generated ? 'alert-row' : ''}>
                <td>{new Date(metric.frame_captured_at).toLocaleString()}</td>
                <td>{metric.peak_pressure.toFixed(1)}</td>
                <td>{metric.contact_area_percent.toFixed(1)}</td>
                <td>
                  {metric.alert_generated ? (
                    <span className="badge alert-badge">Alert</span>
                  ) : (
                    <span className="badge normal-badge">Normal</span>
                  )}
                </td>
                <td>
                  {metric.high_pressure_region ? (
                    <span className="region-info">
                      Area: {metric.high_pressure_region.area} px
                    </span>
                  ) : (
                    <span className="no-region">None</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

function getStartTime(period: TimePeriod): string {
  const now = new Date();
  const start = new Date(now);

  switch (period) {
    case '1h':
      start.setHours(now.getHours() - 1);
      break;
    case '6h':
      start.setHours(now.getHours() - 6);
      break;
    case '24h':
      start.setHours(now.getHours() - 24);
      break;
    case '7d':
      start.setDate(now.getDate() - 7);
      break;
    default:
      start.setHours(now.getHours() - 24);
  }

  return start.toISOString();
}
