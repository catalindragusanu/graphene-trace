import React, { useMemo } from 'react';
import Plot from 'react-plotly.js';
import { FrameSummary } from '../../types/frame';

interface PressureTrendChartProps {
    frames: FrameSummary[];
    currentIndex: number;
}

export const PressureTrendChart: React.FC<PressureTrendChartProps> = ({ frames, currentIndex }) => {
    const chartData = useMemo(() => {
        if (!frames || frames.length === 0) return { x: [], y: [] };

        // Sort frames by time just in case
        const sortedFrames = [...frames].sort((a, b) =>
            new Date(a.captured_at).getTime() - new Date(b.captured_at).getTime()
        );

        const x = sortedFrames.map(f => new Date(f.captured_at));
        const y = sortedFrames.map(f => f.average_pressure || 0);

        return { x, y };
    }, [frames]);

    // Current frame marker
    const currentMarker = useMemo(() => {
        if (!frames[currentIndex]) return null;
        const currentFrame = frames[currentIndex];

        return {
            x: [new Date(currentFrame.captured_at)],
            y: [currentFrame.average_pressure || 0]
        };
    }, [frames, currentIndex]);

    return (
        <div className="trend-chart-container">
            <Plot
                data={[
                    {
                        x: chartData.x,
                        y: chartData.y,
                        type: 'scatter',
                        mode: 'lines',
                        name: 'Avg Pressure',
                        line: { color: '#3b82f6', width: 2 },
                        fill: 'tozeroy',
                        fillcolor: 'rgba(59, 130, 246, 0.1)'
                    },
                    // Current position marker
                    currentMarker ? {
                        x: currentMarker.x,
                        y: currentMarker.y,
                        type: 'scatter',
                        mode: 'markers',
                        name: 'Current',
                        marker: { color: '#ef4444', size: 10, symbol: 'circle' },
                        showlegend: false
                    } : {}
                ]}
                layout={{
                    title: { text: 'Pressure History (Last 2 Hours)', font: { size: 14 } },
                    autosize: true,
                    height: 250,
                    margin: { l: 40, r: 20, t: 40, b: 40 },
                    xaxis: {
                        showgrid: false,
                        zeroline: false,
                        fixedrange: true
                    },
                    yaxis: {
                        title: 'Avg Pressure',
                        range: [0, 255],
                        fixedrange: true
                    },
                    showlegend: false,
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                }}
                config={{ displayModeBar: false }}
                style={{ width: '100%' }}
            />
        </div>
    );
};
