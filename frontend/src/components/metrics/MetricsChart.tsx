import React from 'react';
import Plot from 'react-plotly.js';
import type { PlotData } from 'plotly.js';
import { MetricWithFrame } from '../../types/metric';

interface MetricsChartProps {
  data: MetricWithFrame[];
  yKey: 'peak_pressure' | 'contact_area_percent';
  title: string;
  color?: string;
  thresholdLine?: {
    value: number;
    label: string;
  };
}

export const MetricsChart: React.FC<MetricsChartProps> = ({
  data,
  yKey,
  title,
  color = 'rgb(99, 110, 250)',
  thresholdLine
}) => {
  const timestamps = data.map(m => new Date(m.frame_captured_at));
  const values = data.map(m => m[yKey]);

  const traces: Partial<PlotData>[] = [
    {
      x: timestamps,
      y: values,
      type: 'scatter',
      mode: 'lines+markers',
      name: title,
      line: {
        color: color,
        width: 2
      },
      marker: {
        size: 6,
        color: color
      },
      hovertemplate: '<b>%{x}</b><br>' + title + ': %{y:.1f}<extra></extra>'
    }
  ];

  // Add threshold line if specified
  if (thresholdLine) {
    traces.push({
      x: [timestamps[0], timestamps[timestamps.length - 1]],
      y: [thresholdLine.value, thresholdLine.value],
      type: 'scatter',
      mode: 'lines',
      name: thresholdLine.label,
      line: {
        color: 'rgba(255, 0, 0, 0.5)',
        width: 2,
        dash: 'dash'
      },
      hovertemplate: thresholdLine.label + ': %{y}<extra></extra>'
    });
  }

  return (
    <Plot
      data={traces}
      layout={{
        autosize: true,
        height: 300,
        margin: { l: 60, r: 40, t: 10, b: 60 },
        xaxis: {
          title: 'Time',
          gridcolor: 'rgba(200, 200, 200, 0.3)',
          showgrid: true
        },
        yaxis: {
          title: title,
          gridcolor: 'rgba(200, 200, 200, 0.3)',
          showgrid: true
        },
        hovermode: 'closest',
        showlegend: thresholdLine ? true : false,
        legend: {
          x: 0,
          y: 1,
          bgcolor: 'rgba(255, 255, 255, 0.8)'
        },
        plot_bgcolor: 'rgba(245, 247, 250, 1)',
        paper_bgcolor: 'white'
      }}
      config={{
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['lasso2d', 'select2d']
      }}
      style={{ width: '100%' }}
    />
  );
};
