import { Link } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

export default function Dashboard() {
    const { user } = useAuthStore();

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-8">
                Welcome, {user?.full_name}
            </h1>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <Link
                    to="/map"
                    className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition duration-200"
                >
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-semibold text-gray-800">Interactive Map</h2>
                        <span className="text-3xl">🗺️</span>
                    </div>
                    <p className="text-gray-600">
                        View water-logging incidents and hotspots on an interactive map
                    </p>
                </Link>

                <Link
                    to="/reports/new"
                    className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition duration-200"
                >
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-semibold text-gray-800">Report Incident</h2>
                        <span className="text-3xl">📝</span>
                    </div>
                    <p className="text-gray-600">
                        Submit a new water-logging report with photos and location
                    </p>
                </Link>

                <Link
                    to="/reports"
                    className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition duration-200"
                >
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-semibold text-gray-800">View Reports</h2>
                        <span className="text-3xl">📋</span>
                    </div>
                    <p className="text-gray-600">
                        Browse all water-logging reports and their status
                    </p>
                </Link>

                {(user?.role === 'AUTHORITY' || user?.role === 'ADMIN') && (
                    <Link
                        to="/authority"
                        className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition duration-200"
                    >
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-xl font-semibold text-gray-800">Authority Dashboard</h2>
                            <span className="text-3xl">👮</span>
                        </div>
                        <p className="text-gray-600">
                            Manage reports, update status, and assign agencies
                        </p>
                    </Link>
                )}

                <Link
                    to="/analytics"
                    className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition duration-200"
                >
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-semibold text-gray-800">Ward Analytics</h2>
                        <span className="text-3xl">📊</span>
                    </div>
                    <p className="text-gray-600">
                        View ward-level risk scores and preparedness insights
                    </p>
                </Link>
            </div>

            <div className="mt-12 bg-primary-50 p-6 rounded-lg">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">About This Platform</h2>
                <p className="text-gray-700 mb-4">
                    The Delhi Water-Logging Hotspot Mapping Platform is a civic-technology solution designed to:
                </p>
                <ul className="list-disc list-inside space-y-2 text-gray-700">
                    <li>Collect citizen-reported, geotagged water-logging incidents</li>
                    <li>Visualize incidents and risk zones on an interactive map</li>
                    <li>Predict water-logging-prone areas using open data and analytics</li>
                    <li>Support municipal authority workflows for verification and resolution</li>
                    <li>Generate ward-level preparedness insights</li>
                </ul>
            </div>
        </div>
    );
}
