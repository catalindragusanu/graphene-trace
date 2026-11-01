import React from 'react';

interface RiskGaugeProps {
    score: number;
    level: string;
    color: string;
}

export const RiskGauge: React.FC<RiskGaugeProps> = ({ score, level, color }) => {
    // Calculate gauge rotation (-90deg to 90deg)
    const rotation = -90 + (score / 100) * 180;

    return (
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            padding: '1rem'
        }}>
            <div style={{ position: 'relative', width: 200, height: 120 }}>
                {/* Background arc */}
                <svg width="200" height="120" viewBox="0 0 200 120">
                    {/* Low (green) */}
                    <path
                        d="M 20 100 A 80 80 0 0 1 65 30"
                        fill="none"
                        stroke="#10b981"
                        strokeWidth="20"
                        strokeLinecap="round"
                    />
                    {/* Moderate (yellow) */}
                    <path
                        d="M 65 30 A 80 80 0 0 1 100 20"
                        fill="none"
                        stroke="#eab308"
                        strokeWidth="20"
                        strokeLinecap="round"
                    />
                    {/* High (orange) */}
                    <path
                        d="M 100 20 A 80 80 0 0 1 135 30"
                        fill="none"
                        stroke="#f59e0b"
                        strokeWidth="20"
                        strokeLinecap="round"
                    />
                    {/* Critical (red) */}
                    <path
                        d="M 135 30 A 80 80 0 0 1 180 100"
                        fill="none"
                        stroke="#ef4444"
                        strokeWidth="20"
                        strokeLinecap="round"
                    />
                </svg>

                {/* Needle */}
                <div
                    style={{
                        position: 'absolute',
                        bottom: 10,
                        left: '50%',
                        width: 4,
                        height: 70,
                        background: '#1f2937',
                        transformOrigin: 'bottom center',
                        transform: `translateX(-50%) rotate(${rotation}deg)`,
                        transition: 'transform 0.5s ease',
                        borderRadius: '2px 2px 0 0'
                    }}
                />

                {/* Center dot */}
                <div
                    style={{
                        position: 'absolute',
                        bottom: 5,
                        left: '50%',
                        width: 12,
                        height: 12,
                        background: '#1f2937',
                        borderRadius: '50%',
                        transform: 'translateX(-50%)',
                        border: '2px solid white'
                    }}
                />
            </div>

            {/* Score display */}
            <div style={{ textAlign: 'center', marginTop: '0.5rem' }}>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color }}>{score}</div>
                <div style={{ fontSize: '0.9rem', fontWeight: '600', color, textTransform: 'uppercase' }}>
                    {level}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem' }}>
                    Ulcer Risk Score
                </div>
            </div>
        </div>
    );
};
