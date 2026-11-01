import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Header } from '../components/common/Header';
import { clinicianService } from '../services/clinicianService';
import '../styles/Dashboard.css';

export const ClinicianDashboard: React.FC = () => {
    const navigate = useNavigate();
    const { data: patients, isLoading, error } = useQuery({
        queryKey: ['patients'],
        queryFn: clinicianService.getPatients,
        refetchInterval: 5000 // Poll every 5 seconds for real-time status
    });

    const getStatusColor = (risk: string) => {
        switch (risk) {
            case 'Critical': return '#ef4444'; // Red
            case 'High': return '#f59e0b'; // Orange
            case 'Safe': return '#10b981'; // Green
            default: return '#6b7280'; // Gray
        }
    };

    if (isLoading) {
        return (
            <div className="dashboard">
                <Header />
                <div className="dashboard-content">
                    <div className="loading">Loading patient data...</div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="dashboard">
                <Header />
                <div className="dashboard-content">
                    <div className="error">Error loading patients: {(error as Error).message}</div>
                </div>
            </div>
        );
    }

    return (
        <div className="dashboard">
            <Header />

            <div className="dashboard-content" style={{ display: 'block' }}> {/* Override grid for this page */}
                <div className="dashboard-header" style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <h1 style={{ margin: 0, fontSize: '1.8rem', color: '#1f2937' }}>Command Center</h1>
                        <p style={{ margin: '0.5rem 0 0', color: '#6b7280' }}>
                            Monitoring {patients?.length || 0} active patients
                        </p>
                    </div>
                    <div className="card" style={{ padding: '1rem', display: 'flex', gap: '2rem' }}>
                        <div style={{ textAlign: 'center' }}>
                            <span style={{ display: 'block', fontSize: '1.5rem', fontWeight: 'bold', color: '#ef4444' }}>
                                {patients?.filter(p => p.risk_level === 'Critical').length || 0}
                            </span>
                            <span style={{ fontSize: '0.8rem', color: '#6b7280' }}>Critical</span>
                        </div>
                        <div style={{ textAlign: 'center' }}>
                            <span style={{ display: 'block', fontSize: '1.5rem', fontWeight: 'bold', color: '#f59e0b' }}>
                                {patients?.filter(p => p.risk_level === 'High').length || 0}
                            </span>
                            <span style={{ fontSize: '0.8rem', color: '#6b7280' }}>High Risk</span>
                        </div>
                        <div style={{ textAlign: 'center' }}>
                            <span style={{ display: 'block', fontSize: '1.5rem', fontWeight: 'bold', color: '#10b981' }}>
                                {patients?.filter(p => p.risk_level === 'Safe').length || 0}
                            </span>
                            <span style={{ fontSize: '0.8rem', color: '#6b7280' }}>Safe</span>
                        </div>
                    </div>
                </div>

                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
                    gap: '1.5rem'
                }}>
                    {patients?.map(patient => (
                        <div key={patient.id} className="card" style={{ borderTop: `4px solid ${getStatusColor(patient.risk_level)}` }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                                    {patient.photo_url ? (
                                        <img src={patient.photo_url} alt={patient.name} style={{ width: 50, height: 50, borderRadius: '50%', objectFit: 'cover' }} />
                                    ) : (
                                        <div style={{ width: 50, height: 50, borderRadius: '50%', background: '#eee', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
                                            {patient.name.charAt(0)}
                                        </div>
                                    )}
                                    <div>
                                        <h3 style={{ margin: 0, fontSize: '1.1rem' }}>{patient.name}</h3>
                                        <span style={{ fontSize: '0.8rem', color: '#6b7280' }}>Room {100 + patient.id}</span>
                                    </div>
                                </div>
                                <span style={{
                                    background: getStatusColor(patient.risk_level),
                                    color: 'white',
                                    padding: '4px 8px',
                                    borderRadius: '4px',
                                    fontSize: '0.75rem',
                                    fontWeight: '600'
                                }}>
                                    {patient.risk_level.toUpperCase()}
                                </span>
                            </div>

                            <div className="info-grid">
                                <div className="stat-item">
                                    <span className="stat-label">Max Pressure</span>
                                    <span className="stat-value">{patient.max_pressure}</span>
                                </div>
                                <div className="stat-item">
                                    <span className="stat-label">Last Update</span>
                                    <span className="stat-value" style={{ fontSize: '0.9rem' }}>
                                        {patient.last_updated ? new Date(patient.last_updated).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Never'}
                                    </span>
                                </div>
                            </div>

                            <button style={{
                                width: '100%',
                                marginTop: '1rem',
                                padding: '0.75rem',
                                background: '#f3f4f6',
                                border: 'none',
                                borderRadius: '6px',
                                color: '#4b5563',
                                fontWeight: '600',
                                cursor: 'pointer',
                                transition: 'background 0.2s'
                            }}
                                onMouseOver={(e) => e.currentTarget.style.background = '#e5e7eb'}
                                onMouseOut={(e) => e.currentTarget.style.background = '#f3f4f6'}
                                onClick={() => navigate(`/clinician/patient/${patient.id}`, { state: { patient } })}
                            >
                                View Details
                            </button>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};
