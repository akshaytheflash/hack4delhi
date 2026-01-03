import { useEffect, useState } from 'react';
import { analyticsAPI } from '../../services/api';
import { Ward, WardAnalytics } from '../../types';

export default function WardAnalyticsView() {
    const [wards, setWards] = useState<Ward[]>([]);
    const [selectedWard, setSelectedWard] = useState<WardAnalytics | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadWards();
    }, []);

    const loadWards = async () => {
        try {
            const response = await analyticsAPI.getWards();
            setWards(response.data);
        } catch (error) {
            console.error('Error loading wards:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadWardAnalytics = async (wardId: number) => {
        try {
            const response = await analyticsAPI.getWardAnalytics(wardId);
            setSelectedWard(response.data);
        } catch (error) {
            console.error('Error loading ward analytics:', error);
        }
    };

    const getRiskColor = (score: number) => {
        if (score >= 75) return 'text-red-600';
        if (score >= 50) return 'text-orange-600';
        if (score >= 25) return 'text-yellow-600';
        return 'text-green-600';
    };

    const getRiskCategory = (score: number) => {
        if (score >= 75) return 'CRITICAL';
        if (score >= 50) return 'HIGH';
        if (score >= 25) return 'MEDIUM';
        return 'LOW';
    };

    if (loading) {
        return <div className="text-center py-12">Loading...</div>;
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-8">Ward-Level Analytics</h1>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white shadow-md rounded-lg p-6">
                    <h2 className="text-xl font-bold text-gray-900 mb-4">All Wards</h2>
                    <div className="space-y-2 max-h-[600px] overflow-y-auto">
                        {wards
                            .sort((a, b) => b.risk_score - a.risk_score)
                            .map((ward) => (
                                <div
                                    key={ward.id}
                                    onClick={() => loadWardAnalytics(ward.id)}
                                    className={`p-4 border rounded-lg cursor-pointer hover:bg-gray-50 ${selectedWard?.ward.id === ward.id ? 'border-primary-500 bg-primary-50' : 'border-gray-200'
                                        }`}
                                >
                                    <div className="flex justify-between items-start mb-2">
                                        <div>
                                            <h3 className="font-semibold text-gray-900">{ward.ward_name}</h3>
                                            <p className="text-sm text-gray-600">Ward {ward.ward_number}</p>
                                        </div>
                                        <div className="text-right">
                                            <p className={`text-2xl font-bold ${getRiskColor(ward.risk_score)}`}>
                                                {ward.risk_score.toFixed(1)}
                                            </p>
                                            <p className="text-xs text-gray-500">{getRiskCategory(ward.risk_score)}</p>
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
                                        {ward.elevation_avg && (
                                            <div>Elevation: {ward.elevation_avg.toFixed(1)}m</div>
                                        )}
                                        {ward.slope_avg && (
                                            <div>Slope: {ward.slope_avg.toFixed(2)}°</div>
                                        )}
                                        <div>Incidents: {ward.incident_density.toFixed(2)}/km²</div>
                                    </div>
                                </div>
                            ))}
                    </div>
                </div>

                <div className="bg-white shadow-md rounded-lg p-6">
                    {selectedWard ? (
                        <>
                            <h2 className="text-xl font-bold text-gray-900 mb-4">
                                {selectedWard.ward.ward_name} Details
                            </h2>

                            <div className="space-y-6">
                                <div className="bg-gray-50 p-4 rounded-lg">
                                    <h3 className="font-semibold text-gray-700 mb-2">Risk Assessment</h3>
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-gray-600">Risk Score:</span>
                                        <span className={`text-3xl font-bold ${getRiskColor(selectedWard.ward.risk_score)}`}>
                                            {selectedWard.ward.risk_score.toFixed(1)}
                                        </span>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-4">
                                        <div
                                            className={`h-4 rounded-full ${selectedWard.ward.risk_score >= 75 ? 'bg-red-600' :
                                                selectedWard.ward.risk_score >= 50 ? 'bg-orange-600' :
                                                    selectedWard.ward.risk_score >= 25 ? 'bg-yellow-600' :
                                                        'bg-green-600'
                                                }`}
                                            style={{ width: `${selectedWard.ward.risk_score}%` }}
                                        ></div>
                                    </div>
                                    <p className="text-sm text-gray-600 mt-2">
                                        Category: <span className="font-semibold">{getRiskCategory(selectedWard.ward.risk_score)}</span>
                                    </p>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div className="bg-blue-50 p-4 rounded-lg">
                                        <p className="text-sm text-gray-600">Total Reports</p>
                                        <p className="text-3xl font-bold text-blue-600">{selectedWard.total_reports}</p>
                                    </div>
                                    <div className="bg-red-50 p-4 rounded-lg">
                                        <p className="text-sm text-gray-600">Open Reports</p>
                                        <p className="text-3xl font-bold text-red-600">{selectedWard.open_reports}</p>
                                    </div>
                                    <div className="bg-green-50 p-4 rounded-lg">
                                        <p className="text-sm text-gray-600">Resolved Reports</p>
                                        <p className="text-3xl font-bold text-green-600">{selectedWard.resolved_reports}</p>
                                    </div>
                                    <div className="bg-purple-50 p-4 rounded-lg">
                                        <p className="text-sm text-gray-600">Avg Resolution Time</p>
                                        <p className="text-3xl font-bold text-purple-600">
                                            {selectedWard.avg_resolution_time_hours
                                                ? `${selectedWard.avg_resolution_time_hours.toFixed(1)}h`
                                                : 'N/A'}
                                        </p>
                                    </div>
                                </div>

                                <div className="bg-gray-50 p-4 rounded-lg">
                                    <h3 className="font-semibold text-gray-700 mb-2">Geographic Features</h3>
                                    <div className="space-y-2 text-sm">
                                        {selectedWard.ward.elevation_avg && (
                                            <div className="flex justify-between">
                                                <span className="text-gray-600">Average Elevation:</span>
                                                <span className="font-semibold">{selectedWard.ward.elevation_avg.toFixed(1)} meters</span>
                                            </div>
                                        )}
                                        {selectedWard.ward.slope_avg && (
                                            <div className="flex justify-between">
                                                <span className="text-gray-600">Average Slope:</span>
                                                <span className="font-semibold">{selectedWard.ward.slope_avg.toFixed(2)}°</span>
                                            </div>
                                        )}
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Incident Density:</span>
                                            <span className="font-semibold">{selectedWard.ward.incident_density.toFixed(2)} per km²</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
                                    <h3 className="font-semibold text-yellow-800 mb-2">Preparedness Recommendation</h3>
                                    <p className="text-sm text-yellow-700">
                                        {selectedWard.ward.risk_score >= 75
                                            ? 'CRITICAL: Immediate action required. Deploy emergency response teams and drainage clearing units.'
                                            : selectedWard.ward.risk_score >= 50
                                                ? 'HIGH: Proactive monitoring needed. Ensure drainage systems are clear and emergency teams are on standby.'
                                                : selectedWard.ward.risk_score >= 25
                                                    ? 'MEDIUM: Regular monitoring recommended. Schedule routine drainage maintenance.'
                                                    : 'LOW: Standard monitoring sufficient. Continue regular maintenance schedules.'}
                                    </p>
                                </div>
                            </div>
                        </>
                    ) : (
                        <div className="text-center text-gray-500 py-12">
                            Select a ward to view detailed analytics
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
