import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { reportsAPI, authorityAPI } from '../../services/api';
import { Report } from '../../types';
import { useAuthStore } from '../../store/authStore';

export default function AuthorityDashboard() {
    const { user } = useAuthStore();
    const navigate = useNavigate();
    const [reports, setReports] = useState<Report[]>([]);
    const [selectedReport, setSelectedReport] = useState<Report | null>(null);
    const [updateData, setUpdateData] = useState({
        status: '',
        severity: '',
        assigned_agency: '',
        notes: '',
    });
    const [resolutionImage, setResolutionImage] = useState<File | null>(null);

    useEffect(() => {
        if (user?.role !== 'AUTHORITY' && user?.role !== 'ADMIN') {
            navigate('/');
            return;
        }
        loadReports();
    }, [user]);

    const loadReports = async () => {
        try {
            const response = await reportsAPI.getAll({ limit: 100 });
            setReports(response.data.reports);
        } catch (error) {
            console.error('Error loading reports:', error);
        }
    };

    const handleUpdateReport = async () => {
        if (!selectedReport) return;

        try {
            await authorityAPI.updateReport(selectedReport.id, {
                status: updateData.status || undefined,
                severity: updateData.severity || undefined,
                assigned_agency: updateData.assigned_agency || undefined,
                notes: updateData.notes || undefined,
            });

            if (resolutionImage) {
                await authorityAPI.uploadResolutionImage(selectedReport.id, resolutionImage);
            }

            alert('Report updated successfully');
            setSelectedReport(null);
            setUpdateData({ status: '', severity: '', assigned_agency: '', notes: '' });
            setResolutionImage(null);
            loadReports();
        } catch (error: any) {
            alert(error.response?.data?.detail || 'Failed to update report');
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-8">Authority Dashboard</h1>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white shadow-md rounded-lg p-6">
                    <h2 className="text-xl font-bold text-gray-900 mb-4">Reports</h2>
                    <div className="space-y-2 max-h-[600px] overflow-y-auto">
                        {reports.map((report) => (
                            <div
                                key={report.id}
                                onClick={() => {
                                    setSelectedReport(report);
                                    setUpdateData({
                                        status: report.status,
                                        severity: report.severity,
                                        assigned_agency: report.assigned_agency || '',
                                        notes: '',
                                    });
                                }}
                                className={`p-4 border rounded-lg cursor-pointer hover:bg-gray-50 ${selectedReport?.id === report.id ? 'border-primary-500 bg-primary-50' : 'border-gray-200'
                                    }`}
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <h3 className="font-semibold text-gray-900">{report.title}</h3>
                                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${report.status === 'OPEN' ? 'bg-red-100 text-red-800' :
                                            report.status === 'IN_PROGRESS' ? 'bg-yellow-100 text-yellow-800' :
                                                'bg-green-100 text-green-800'
                                        }`}>
                                        {report.status}
                                    </span>
                                </div>
                                <p className="text-sm text-gray-600 line-clamp-2">{report.description}</p>
                                <p className="text-xs text-gray-500 mt-2">
                                    {new Date(report.created_at).toLocaleDateString()}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="bg-white shadow-md rounded-lg p-6">
                    {selectedReport ? (
                        <>
                            <h2 className="text-xl font-bold text-gray-900 mb-4">Update Report</h2>

                            <div className="space-y-4">
                                <div>
                                    <h3 className="font-semibold text-gray-900 mb-2">{selectedReport.title}</h3>
                                    <p className="text-gray-600 text-sm mb-4">{selectedReport.description}</p>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Status
                                    </label>
                                    <select
                                        value={updateData.status}
                                        onChange={(e) => setUpdateData({ ...updateData, status: e.target.value })}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                    >
                                        <option value="OPEN">Open</option>
                                        <option value="IN_PROGRESS">In Progress</option>
                                        <option value="RESOLVED">Resolved</option>
                                        <option value="CLOSED">Closed</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Severity
                                    </label>
                                    <select
                                        value={updateData.severity}
                                        onChange={(e) => setUpdateData({ ...updateData, severity: e.target.value })}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                    >
                                        <option value="LOW">Low</option>
                                        <option value="MEDIUM">Medium</option>
                                        <option value="HIGH">High</option>
                                        <option value="CRITICAL">Critical</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Assign Agency
                                    </label>
                                    <select
                                        value={updateData.assigned_agency}
                                        onChange={(e) => setUpdateData({ ...updateData, assigned_agency: e.target.value })}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                    >
                                        <option value="">Not Assigned</option>
                                        <option value="MCD">MCD</option>
                                        <option value="PWD">PWD</option>
                                        <option value="NDMC">NDMC</option>
                                        <option value="DDA">DDA</option>
                                        <option value="OTHER">Other</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Notes
                                    </label>
                                    <textarea
                                        value={updateData.notes}
                                        onChange={(e) => setUpdateData({ ...updateData, notes: e.target.value })}
                                        rows={3}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                        placeholder="Add notes about this update..."
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Resolution Photo
                                    </label>
                                    <input
                                        type="file"
                                        accept="image/*"
                                        onChange={(e) => setResolutionImage(e.target.files?.[0] || null)}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                    />
                                </div>

                                <button
                                    onClick={handleUpdateReport}
                                    className="w-full bg-primary-600 text-white py-2 rounded-md hover:bg-primary-700"
                                >
                                    Update Report
                                </button>
                            </div>
                        </>
                    ) : (
                        <div className="text-center text-gray-500 py-12">
                            Select a report to update
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
