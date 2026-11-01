import React, { useState, useEffect } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Header } from '../components/common/Header';
import { useAuth } from '../components/auth/AuthContext';
import { PressureHeatmap } from '../components/heatmap/PressureHeatmap';
import { TimelineScrubber } from '../components/heatmap/TimelineScrubber';
import { PressureTrendChart } from '../components/heatmap/PressureTrendChart';
import { RiskGauge } from '../components/ml/RiskGauge';
import { MovementQualityDisplay } from '../components/ml/MovementQualityDisplay';
import { useFrames, useFrame } from '../hooks/useFrames';
import { mlService } from '../services/mlService';
import '../styles/Dashboard.css';

export const PatientDashboard: React.FC = () => {
  const { user: authUser } = useAuth();
  const { id } = useParams<{ id: string }>();
  const { state } = useLocation();

  // If we have an ID (clinician view), use the passed patient state or fallback
  // In a real app we would fetch the patient details if state is missing
  const patientUser = id ? state?.patient : authUser;
  const targetUserId = id ? parseInt(id) : undefined;

  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  // Fetch frames list
  const { data: frames, isLoading: framesLoading, error: framesError } = useFrames({
    limit: 100,
    user_id: targetUserId
  });

  // Fetch ML data
  const { data: riskData } = useQuery({
    queryKey: ['risk', targetUserId],
    queryFn: () => mlService.getRiskScore(targetUserId),
    refetchInterval: 60000, // Refresh every minute
    enabled: !!frames && frames.length > 0
  });

  const { data: movementData } = useQuery({
    queryKey: ['movements', targetUserId],
    queryFn: () => mlService.getMovementSummary(targetUserId, 24),
    refetchInterval: 60000,
    enabled: !!frames && frames.length > 0
  });

  // Animation effect
  useEffect(() => {
    let interval: number;
    if (isPlaying && frames && frames.length > 0) {
      interval = window.setInterval(() => {
        setCurrentIndex((prev) => (prev + 1) % frames.length);
      }, 500); // Update every 500ms
    }
    return () => clearInterval(interval);
  }, [isPlaying, frames]);

  const togglePlay = () => setIsPlaying(!isPlaying);

  // Get current frame ID
  const currentFrameId = frames?.[currentIndex]?.id;

  // Fetch current frame detail (with pressure data)
  const { data: frameDetail, isLoading: frameLoading } = useFrame(currentFrameId || 0);

  if (framesLoading) {
    return (
      <div className="dashboard">
        <Header />
        <div className="loading">Loading frames...</div>
      </div>
    );
  }

  if (framesError) {
    return (
      <div className="dashboard">
        <Header />
        <div className="error">Error loading frames: {(framesError as Error).message}</div>
      </div>
    );
  }

  if (!frames || frames.length === 0) {
    return (
      <div className="dashboard">
        <Header />
        <div className="empty-state">
          <h2>No Data Available</h2>
          <p>No pressure frames found for your account.</p>
          <p>Please contact your clinician if you expect to see data here.</p>
        </div>
      </div>
    );
  }

  // Calculate stats
  const maxPressure = frameDetail ? Math.max(...frameDetail.data.flat()) : 0;
  const avgPressure = frameDetail ? Math.round(frameDetail.data.flat().reduce((a, b) => a + b, 0) / frameDetail.data.flat().length) : 0;

  const getRiskLevel = (max: number) => {
    if (max > 200) return { label: 'CRITICAL', color: '#ef4444' };
    if (max > 150) return { label: 'High', color: '#f59e0b' };
    return { label: 'Normal', color: '#10b981' };
  };

  const risk = getRiskLevel(maxPressure);

  // Improved Repositioning Logic
  // We scan backwards from current index to find a significant change in pressure profile
  const getTimeSinceReposition = () => {
    if (!frames || frames.length === 0 || !frameDetail) return 0;

    // Default to time of current frame if no movement found
    let lastMoveTime = new Date(frameDetail.captured_at).getTime();

    // Look back up to 20 frames (~40 mins)
    for (let i = currentIndex; i > Math.max(0, currentIndex - 20); i--) {
      const current = frames[i];
      const prev = frames[i - 1];

      if (!prev) continue;

      // If max pressure changed by > 20 units, assume movement
      const delta = Math.abs((current.max_pressure || 0) - (prev.max_pressure || 0));
      if (delta > 20) {
        lastMoveTime = new Date(current.captured_at).getTime();
        break;
      }
    }

    // Calculate minutes difference
    const currentFrameTime = new Date(frameDetail.captured_at).getTime();
    return Math.max(0, Math.floor((currentFrameTime - lastMoveTime) / 60000));
  };

  const timeSinceReposition = getTimeSinceReposition();

  return (
    <div className="dashboard">
      <Header />

      <div className="dashboard-content">
        {/* Sidebar */}
        <div className="dashboard-sidebar">
          {/* Profile Card */}
          <div className="card profile-section">
            {patientUser?.photo_url ? (
              <img src={patientUser.photo_url} alt={patientUser.name} className="profile-photo" />
            ) : (
              <div className="profile-photo" style={{ background: '#eee', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {patientUser?.name.charAt(0)}
              </div>
            )}
            <div className="profile-details">
              <h3>{patientUser?.name}</h3>
              <p><strong>DOB:</strong> {patientUser?.date_of_birth || 'Not set'}</p>
              <p><strong>Condition:</strong><br />{patientUser?.medical_condition || 'None listed'}</p>
            </div>
          </div>

          {/* Stats Card */}
          <div className="card">
            <h3>Real-time Stats</h3>
            <div className="info-grid">
              <div className="stat-item">
                <span className="stat-label">Max Pressure</span>
                <span className="stat-value" style={{ color: risk.color }}>{maxPressure}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Avg Pressure</span>
                <span className="stat-value">{avgPressure}</span>
              </div>
              <div className="stat-item" style={{ gridColumn: '1 / -1' }}>
                <span className="stat-label">Risk Level</span>
                <span className="stat-value" style={{ color: risk.color }}>{risk.label}</span>
              </div>
              {/* Repositioning Timer */}
              <div className="stat-item" style={{ gridColumn: '1 / -1', borderTop: '1px solid #eee', paddingTop: '1rem', marginTop: '0.5rem' }}>
                <span className="stat-label">Time Since Reposition</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span className="stat-value" style={{ color: timeSinceReposition > 120 ? '#ef4444' : '#1f2937' }}>
                    {Math.floor(timeSinceReposition / 60)}h {timeSinceReposition % 60}m
                  </span>
                  {timeSinceReposition > 120 && <span style={{ fontSize: '0.8rem', color: '#ef4444' }}> (Overdue!)</span>}
                </div>
              </div>
            </div>
          </div>

          {/* Frame Info Card */}
          {frameDetail && (
            <div className="card">
              <h3>Frame Details</h3>
              <div className="info-grid">
                <div className="stat-item" style={{ gridColumn: '1 / -1' }}>
                  <span className="stat-label">Captured At</span>
                  <span className="stat-value" style={{ fontSize: '1rem' }}>
                    {new Date(frameDetail.captured_at).toLocaleTimeString()}
                  </span>
                  <span className="stat-label">{new Date(frameDetail.captured_at).toLocaleDateString()}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Frame ID</span>
                  <span className="stat-value">{frameDetail.id}</span>
                </div>
              </div>
            </div>
          )}

          {/* Risk Score Card */}
          {riskData && (
            <div className="card">
              <h3>Ulcer Risk Analysis</h3>
              <RiskGauge
                score={riskData.score}
                level={riskData.level}
                color={riskData.color}
              />
            </div>
          )}

          {/* Movement Quality Card */}
          {movementData && (
            <div className="card">
              <MovementQualityDisplay summary={movementData} />
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="dashboard-main">

          {/* Alarm Banner */}
          {maxPressure > 200 && (
            <div className="alarm-banner">
              <span className="alarm-icon">⚠️</span>
              <div className="alarm-content">
                <strong>CRITICAL PRESSURE ALERT</strong>
                <p>High pressure detected! Immediate repositioning required.</p>
              </div>
            </div>
          )}

          {/* Heatmap Card */}
          <div className="card">
            <div className="timeline-header" style={{ marginBottom: 0 }}>
              <h2>Pressure Map</h2>
              <button
                className={`play-button ${isPlaying ? 'active' : ''}`}
                onClick={togglePlay}
              >
                {isPlaying ? '⏸ Pause' : '▶ Play Simulation'}
              </button>
            </div>

            <div className="heatmap-section">
              {frameLoading ? (
                <div className="loading">Loading frame data...</div>
              ) : frameDetail ? (
                <PressureHeatmap frame={frameDetail} />
              ) : (
                <div className="error">Unable to load frame data</div>
              )}
            </div>
          </div>

          {/* Timeline Card */}
          <div className="card">
            <h3>Timeline</h3>
            <TimelineScrubber
              frames={frames}
              currentIndex={currentIndex}
              onIndexChange={setCurrentIndex}
            />
            {/* Historical Trend Chart */}
            <div style={{ marginTop: '2rem', paddingTop: '2rem', borderTop: '1px solid #f3f4f6' }}>
              {frames && (
                <PressureTrendChart
                  frames={frames}
                  currentIndex={currentIndex}
                />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
