import React, { useState } from 'react';
import { useAuth } from '../components/auth/AuthContext';
import { useFrames, useFrame } from '../hooks/useFrames';
import { useComments } from '../hooks/useComments';
import { Header } from '../components/common/Header';
import { PressureHeatmap } from '../components/heatmap/PressureHeatmap';
import { TimelineScrubber } from '../components/heatmap/TimelineScrubber';
import { MetricsDashboard } from '../components/metrics/MetricsDashboard';
import { AlertsList } from '../components/alerts/AlertsList';
import { CommentThread } from '../components/comments/CommentThread';
import { CommentForm } from '../components/comments/CommentForm';
import '../styles/EnhancedDashboard.css';

type ViewMode = 'heatmap' | 'metrics' | 'alerts';

export const EnhancedPatientDashboard: React.FC = () => {
  const { user } = useAuth();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [viewMode, setViewMode] = useState<ViewMode>('heatmap');
  const [showComments, setShowComments] = useState(true);
  const [replyToCommentId, setReplyToCommentId] = useState<number | null>(null);

  const { data: frames, isLoading: framesLoading, error: framesError } = useFrames({ limit: 500 });

  const currentFrameId = frames?.[currentIndex]?.id;
  const {
    data: frameDetail,
    isLoading: frameLoading,
    error: frameError,
  } = useFrame(currentFrameId || 0);

  const { data: comments, isLoading: commentsLoading } = useComments(currentFrameId || 0);

  const handleAlertClick = (frameId: number) => {
    const index = frames?.findIndex(f => f.id === frameId);
    if (index !== undefined && index !== -1) {
      setCurrentIndex(index);
      setViewMode('heatmap');
    }
  };

  const handleReply = (parentId: number) => {
    setReplyToCommentId(parentId);
  };

  const handleCommentSuccess = () => {
    setReplyToCommentId(null);
  };

  if (framesLoading) {
    return (
      <div className="enhanced-dashboard loading">
        <Header />
        <div className="loading-message">Loading frames...</div>
      </div>
    );
  }

  if (framesError) {
    return (
      <div className="enhanced-dashboard error">
        <Header />
        <div className="error-message">Failed to load frames. Please try again.</div>
      </div>
    );
  }

  if (!frames || frames.length === 0) {
    return (
      <div className="enhanced-dashboard empty">
        <Header />
        <div className="empty-message">No pressure data available yet.</div>
      </div>
    );
  }

  const currentFrame = frames[currentIndex];

  return (
    <div className="enhanced-dashboard">
      <Header />

      <div className="dashboard-content">
        {/* Left Sidebar: Navigation and Info */}
        <aside className="sidebar-left">
          <div className="user-info">
            <h3>Welcome, {user?.name}</h3>
            <p className="user-role">{user?.role}</p>
          </div>

          <div className="view-selector">
            <h4>View Mode</h4>
            <div className="view-buttons">
              <button
                className={`view-btn ${viewMode === 'heatmap' ? 'active' : ''}`}
                onClick={() => setViewMode('heatmap')}
              >
                Heatmap
              </button>
              <button
                className={`view-btn ${viewMode === 'metrics' ? 'active' : ''}`}
                onClick={() => setViewMode('metrics')}
              >
                Metrics
              </button>
              <button
                className={`view-btn ${viewMode === 'alerts' ? 'active' : ''}`}
                onClick={() => setViewMode('alerts')}
              >
                Alerts
              </button>
            </div>
          </div>

          {viewMode === 'heatmap' && (
            <>
              <div className="frame-info">
                <h4>Current Frame</h4>
                <div className="info-item">
                  <span className="label">Frame:</span>
                  <span className="value">{currentIndex + 1} / {frames.length}</span>
                </div>
                <div className="info-item">
                  <span className="label">Time:</span>
                  <span className="value">
                    {new Date(currentFrame.captured_at).toLocaleString()}
                  </span>
                </div>
                <div className="info-item">
                  <span className="label">Alert:</span>
                  <span className={`badge ${currentFrame.has_alerts ? 'alert' : 'normal'}`}>
                    {currentFrame.has_alerts ? 'Yes' : 'No'}
                  </span>
                </div>
              </div>

              <div className="timeline-container">
                <h4>Timeline Navigation</h4>
                <TimelineScrubber
                  frames={frames}
                  currentIndex={currentIndex}
                  onIndexChange={setCurrentIndex}
                />
              </div>
            </>
          )}
        </aside>

        {/* Main Content Area */}
        <main className="main-content">
          {viewMode === 'heatmap' && (
            <div className="heatmap-view">
              {frameLoading && <div className="loading-indicator">Loading frame data...</div>}
              {frameError && <div className="error-indicator">Failed to load frame data</div>}
              {frameDetail && (
                <PressureHeatmap
                  frame={frameDetail}
                  highlightRegion={currentFrame.has_alerts ? undefined : undefined}
                />
              )}
            </div>
          )}

          {viewMode === 'metrics' && (
            <div className="metrics-view">
              <MetricsDashboard />
            </div>
          )}

          {viewMode === 'alerts' && (
            <div className="alerts-view">
              <AlertsList onAlertClick={handleAlertClick} />
            </div>
          )}
        </main>

        {/* Right Sidebar: Comments (only visible in heatmap view) */}
        {viewMode === 'heatmap' && (
          <aside className="sidebar-right">
            <div className="comments-section">
              <div className="comments-header">
                <h4>Comments</h4>
                <button
                  className="toggle-comments-btn"
                  onClick={() => setShowComments(!showComments)}
                >
                  {showComments ? 'Hide' : 'Show'}
                </button>
              </div>

              {showComments && (
                <>
                  <div className="comment-form-container">
                    {replyToCommentId ? (
                      <>
                        <CommentForm
                          frameId={currentFrameId || 0}
                          parentCommentId={replyToCommentId}
                          onSuccess={handleCommentSuccess}
                          onCancel={() => setReplyToCommentId(null)}
                        />
                      </>
                    ) : (
                      <CommentForm
                        frameId={currentFrameId || 0}
                        onSuccess={handleCommentSuccess}
                      />
                    )}
                  </div>

                  <div className="comment-thread-container">
                    {commentsLoading ? (
                      <div className="loading-comments">Loading comments...</div>
                    ) : (
                      <CommentThread
                        comments={comments || []}
                        onReply={handleReply}
                      />
                    )}
                  </div>
                </>
              )}
            </div>
          </aside>
        )}
      </div>
    </div>
  );
};
