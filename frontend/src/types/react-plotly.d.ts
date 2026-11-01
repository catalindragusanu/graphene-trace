declare module 'react-plotly.js' {
    import * as Plotly from 'plotly.js';
    import * as React from 'react';

    export interface PlotParams {
        data: Plotly.Data[];
        layout: Partial<Plotly.Layout>;
        config?: Partial<Plotly.Config>;
        frames?: Plotly.Frame[];
        style?: React.CSSProperties;
        onInitialized?: (figure: Readonly<Plotly.Figure>, graphDiv: Readonly<HTMLElement>) => void;
        onUpdate?: (figure: Readonly<Plotly.Figure>, graphDiv: Readonly<HTMLElement>) => void;
        networkStatus?: (status: string) => void;
        className?: string;
        useResizeHandler?: boolean;
        debug?: boolean;
        divId?: string;
    }

    class Plot extends React.Component<PlotParams> { }
    export default Plot;
}
