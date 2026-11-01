export interface PatientSummary {
    id: number;
    name: string;
    email: string;
    photo_url?: string;
    medical_condition?: string;
    last_updated?: string;
    risk_level: 'Safe' | 'High' | 'Critical' | 'Unknown';
    avg_pressure: number;
    max_pressure: number;
}
