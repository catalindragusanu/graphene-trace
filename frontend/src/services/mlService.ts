import api from './api';

export interface RiskScore {
    score: number;
    level: string;
    color: string;
    factors: {
        max_pressure_factor: number;
        avg_pressure_factor: number;
        reposition_factor: number;
        variance_factor: number;
        frames_analyzed: number;
    };
    calculated_at: string;
}

export interface MovementAnalysisResult {
    message: string;
    frames_analyzed?: number;
    frames_found?: number;
    movements_detected: number;
    macro_movements?: number;
    micro_movements?: number;
}

export interface MovementSummary {
    total_movements: number;
    macro_movements: number;
    micro_movements: number;
    avg_quality_score: number;
    last_macro_movement: string | null;
    time_since_last_macro: number | null;
}

export const mlService = {
    async getRiskScore(userId?: number): Promise<RiskScore> {
        const params = userId ? { user_id: userId } : {};
        const response = await api.get<RiskScore>('/api/risk/current', { params });
        return response.data;
    },

    async getMovementSummary(userId?: number, hours: number = 24): Promise<MovementSummary> {
        const params = userId ? { user_id: userId, hours } : { hours };
        const response = await api.get<MovementSummary>('/api/movements/summary', { params });
        return response.data;
    },

    async analyzeMovements(userId?: number, hours: number = 24): Promise<MovementAnalysisResult> {
        const params = userId ? { user_id: userId, hours } : { hours };
        const response = await api.post<MovementAnalysisResult>('/api/movements/analyze', null, { params });
        return response.data;
    }
};
