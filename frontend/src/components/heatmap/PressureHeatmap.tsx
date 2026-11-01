import React from 'react';
import Plot from 'react-plotly.js';
import { Frame } from '../../types/frame';
import { HighPressureRegion } from '../../types/metric';

interface PressureHeatmapProps {
  frame: Frame;
  highlightRegion?: HighPressureRegion | null;
}

export const PressureHeatmap: React.FC<PressureHeatmapProps> = ({ frame, highlightRegion }) => {
  // Frame data is already a 32x32 matrix
  const matrix = frame.data;

  // Create shape for high-pressure region overlay
  const shapes = highlightRegion ? [{
    type: 'rect' as const,
    x0: highlightRegion.x1 - 0.5,
    y0: highlightRegion.y1 - 0.5,
    x1: highlightRegion.x2 + 0.5,
    y1: highlightRegion.y2 + 0.5,
    line: {
      color: 'red',
      width: 3
    },
    fillcolor: 'transparent'
  }] : [];

  return (
    <div className="heatmap-container">
      <Plot
        data={[{
          z: matrix,
          type: 'heatmap' as const,
          colorscale: [
            [0, 'rgb(0, 0, 255)'],      // Blue - low pressure
            [0.4, 'rgb(0, 255, 0)'],    // Green - moderate
            [0.7, 'rgb(255, 255, 0)'],  // Yellow - elevated
            [0.85, 'rgb(255, 165, 0)'], // Orange - high
            [1, 'rgb(255, 0, 0)']       // Red - critical
          ],
          colorbar: {
            title: { text: 'Pressure' },
            thickness: 20,
            len: 0.7
          },
          hovertemplate: 'Row: %{y}<br>Col: %{x}<br>Pressure: %{z}<extra></extra>',
        }]}
        layout={{
          title: {
            text: `Pressure Map - ${new Date(frame.captured_at).toLocaleString()}`,
            font: { size: 16 }
          },
          xaxis: {
            title: 'Column',
            showgrid: false,
            zeroline: false
          },
          yaxis: {
            title: 'Row',
            showgrid: false,
            zeroline: false,
            autorange: 'reversed' as const  // Flip Y axis
          },
          shapes: shapes,
          width: 600,
          height: 600,
          margin: { l: 60, r: 60, t: 80, b: 60 }
        }}
        config={{
          displayModeBar: true,
          displaylogo: false,
          modeBarButtonsToRemove: ['lasso2d', 'select2d']
        }}
      />
    </div>
  );
};
