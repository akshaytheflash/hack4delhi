import { Link } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

export default function Navbar() {
    const { user, logout } = useAuthStore();

    return (
        <nav className="bg-primary-600 text-white shadow-lg">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    <div className="flex items-center space-x-8">
                        <Link to="/" className="text-xl font-bold">
                            Delhi Water-Logging Platform
                        </Link>
                        <div className="hidden md:flex space-x-4">
                            <Link to="/map" className="hover:bg-primary-700 px-3 py-2 rounded-md">
                                Map
                            </Link>
                            <Link to="/reports" className="hover:bg-primary-700 px-3 py-2 rounded-md">
                                Reports
                            </Link>
                            {user?.role === 'AUTHORITY' || user?.role === 'ADMIN' ? (
                                <Link to="/authority" className="hover:bg-primary-700 px-3 py-2 rounded-md">
                                    Authority Dashboard
                                </Link>
                            ) : null}
                            <Link to="/analytics" className="hover:bg-primary-700 px-3 py-2 rounded-md">
                                Analytics
                            </Link>
                        </div>
                    </div>
                    <div className="flex items-center space-x-4">
                        <span className="text-sm">
                            {user?.full_name} ({user?.role})
                        </span>
                        <button
                            onClick={logout}
                            className="bg-primary-700 hover:bg-primary-800 px-4 py-2 rounded-md text-sm"
                        >
                            Logout
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
}
