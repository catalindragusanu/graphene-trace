import React from 'react';

interface MovementQualityDisplayProps {
    summary: {
        total_movements: number;
        macro_movements: number;
        micro_movements: number;
        avg_quality_score: number;
        last_macro_movement: string | null;
        time_since_last_macro: number | null;
    };
}

export const MovementQualityDisplay: React.FC<MovementQualityDisplayProps> = ({ summary }) => {
    const macroPercentage = summary.total_movements > 0
        ? Math.round((summary.macro_movements / summary.total_movements) * 100)
        : 0;

    const getQualityColor = (score: number) => {
        if (score >= 0.7) return '#10b981';
        if (score >= 0.4) return '#f59e0b';
        return '#ef4444';
    };

    return (
        <div style={{ padding: '1rem' }}>
            <h4 style={{ margin: '0 0 1rem 0', fontSize: '1rem', color: '#1f2937' }}>
                Movement Quality (24h)
            </h4>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                <div style={{ textAlign: 'center', padding: '0.75rem', background: '#f9fafb', borderRadius: '8px' }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#10b981' }}>
                        {summary.macro_movements}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Effective</div>
                </div>
                <div style={{ textAlign: 'center', padding: '0.75rem', background: '#f9fafb', borderRadius: '8px' }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#f59e0b' }}>
                        {summary.micro_movements}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Ineffective</div>
                </div>
            </div>

            {/* Quality bar */}
            <div style={{ marginBottom: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>Effectiveness</span>
                    <span style={{ fontSize: '0.75rem', fontWeight: '600', color: getQualityColor(summary.avg_quality_score) }}>
                        {macroPercentage}%
                    </span>
                </div>
                <div style={{
                    width: '100%',
                    height: '8px',
                    background: '#e5e7eb',
                    borderRadius: '4px',
                    overflow: 'hidden'
                }}>
                    <div style={{
                        width: `${macroPercentage}%`,
                        height: '100%',
                        background: getQualityColor(summary.avg_quality_score),
                        transition: 'width 0.3s ease'
                    }} />
                </div>
            </div>

            {/* Last effective movement */}
            {summary.last_macro_movement && (
                <div style={{
                    padding: '0.75rem',
                    background: summary.time_since_last_macro && summary.time_since_last_macro > 120 ? '#fef2f2' : '#f0fdf4',
                    borderRadius: '6px',
                    border: `1px solid ${summary.time_since_last_macro && summary.time_since_last_macro > 120 ? '#fecaca' : '#bbf7d0'}`
                }}>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280', marginBottom: '0.25rem' }}>
                        Last Effective Reposition
                    </div>
                    <div style={{ fontSize: '0.9rem', fontWeight: '600', color: '#1f2937' }}>
                        {summary.time_since_last_macro} minutes ago
                    </div>
                    {summary.time_since_last_macro && summary.time_since_last_macro > 120 && (
                        <div style={{ fontSize: '0.75rem', color: '#ef4444', marginTop: '0.25rem' }}>
                            ⚠️ Overdue for repositioning
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};
