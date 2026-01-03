import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { reportsAPI } from '../../services/api';
import { Report } from '../../types';

const getSeverityBadge = (severity: string) => {
    const colors = {
        CRITICAL: 'bg-red-100 text-red-800',
        HIGH: 'bg-orange-100 text-orange-800',
        MEDIUM: 'bg-yellow-100 text-yellow-800',
        LOW: 'bg-green-100 text-green-800',
    };
    return colors[severity as keyof typeof colors] || 'bg-gray-100 text-gray-800';
};

const getStatusBadge = (status: string) => {
    const colors = {
        OPEN: 'bg-red-100 text-red-800',
        IN_PROGRESS: 'bg-yellow-100 text-yellow-800',
        RESOLVED: 'bg-green-100 text-green-800',
        CLOSED: 'bg-gray-100 text-gray-800',
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800';
};

export default function ReportList() {
    const [reports, setReports] = useState<Report[]>([]);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({
        status: '',
        severity: '',
    });
    const [page, setPage] = useState(1);
    const [total, setTotal] = useState(0);

    useEffect(() => {
        loadReports();
    }, [filters, page]);

    const loadReports = async () => {
        setLoading(true);
        try {
            const response = await reportsAPI.getAll({
                skip: (page - 1) * 20,
                limit: 20,
                status: filters.status || undefined,
                severity: filters.severity || undefined,
            });
            setReports(response.data.reports);
            setTotal(response.data.total);
        } catch (error) {
            console.error('Error loading reports:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold text-gray-900">Water-Logging Reports</h1>
                <Link
                    to="/reports/new"
                    className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700"
                >
                    + New Report
                </Link>
            </div>

            <div className="bg-white shadow-md rounded-lg p-4 mb-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Status
                        </label>
                        <select
                            value={filters.status}
                            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md"
                        >
                            <option value="">All</option>
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
                            value={filters.severity}
                            onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md"
                        >
                            <option value="">All</option>
                            <option value="LOW">Low</option>
                            <option value="MEDIUM">Medium</option>
                            <option value="HIGH">High</option>
                            <option value="CRITICAL">Critical</option>
                        </select>
                    </div>

                    <div className="flex items-end">
                        <button
                            onClick={() => setFilters({ status: '', severity: '' })}
                            className="w-full bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300"
                        >
                            Clear Filters
                        </button>
                    </div>
                </div>
            </div>

            {loading ? (
                <div className="text-center py-12">Loading...</div>
            ) : (
                <>
                    <div className="space-y-4">
                        {reports.map((report) => (
                            <Link
                                key={report.id}
                                to={`/reports/${report.id}`}
                                className="block bg-white shadow-md rounded-lg p-6 hover:shadow-lg transition duration-200"
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <h2 className="text-xl font-semibold text-gray-900">{report.title}</h2>
                                    <div className="flex space-x-2">
                                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusBadge(report.status)}`}>
                                            {report.status}
                                        </span>
                                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getSeverityBadge(report.severity)}`}>
                                            {report.severity}
                                        </span>
                                    </div>
                                </div>

                                <p className="text-gray-600 mb-4 line-clamp-2">{report.description}</p>

                                <div className="flex items-center justify-between text-sm text-gray-500">
                                    <div className="flex items-center space-x-4">
                                        <span>📍 {report.address || `${report.latitude.toFixed(4)}, ${report.longitude.toFixed(4)}`}</span>
                                        <span>👍 {report.upvote_count} upvotes</span>
                                        <span>💬 {report.comment_count} comments</span>
                                    </div>
                                    <span>{new Date(report.created_at).toLocaleDateString()}</span>
                                </div>
                            </Link>
                        ))}
                    </div>

                    {reports.length === 0 && (
                        <div className="text-center py-12 text-gray-500">
                            No reports found. Try adjusting your filters.
                        </div>
                    )}

                    <div className="mt-8 flex justify-center space-x-2">
                        <button
                            onClick={() => setPage(Math.max(1, page - 1))}
                            disabled={page === 1}
                            className="px-4 py-2 bg-gray-200 rounded-md disabled:opacity-50"
                        >
                            Previous
                        </button>
                        <span className="px-4 py-2">
                            Page {page} of {Math.ceil(total / 20)}
                        </span>
                        <button
                            onClick={() => setPage(page + 1)}
                            disabled={page >= Math.ceil(total / 20)}
                            className="px-4 py-2 bg-gray-200 rounded-md disabled:opacity-50"
                        >
                            Next
                        </button>
                    </div>
                </>
            )}
        </div>
    );
}
