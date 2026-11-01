import api from './api';
import { PatientSummary } from '../types/clinician';

export const clinicianService = {
    getPatients: async (): Promise<PatientSummary[]> => {
        const response = await api.get<PatientSummary[]>('/api/users/patients');
        return response.data;
    }
};
