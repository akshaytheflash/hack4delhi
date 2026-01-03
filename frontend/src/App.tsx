import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useAuthStore } from './store/authStore';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import Dashboard from './components/Dashboard/Dashboard';
import MapView from './components/Map/MapView';
import ReportForm from './components/Report/ReportForm';
import ReportList from './components/Report/ReportList';
import ReportDetail from './components/Report/ReportDetail';
import AuthorityDashboard from './components/Authority/AuthorityDashboard';
import WardAnalyticsView from './components/Analytics/WardAnalytics';
import Navbar from './components/Layout/Navbar';

function App() {
    const { isAuthenticated, isLoading, loadUser } = useAuthStore();

    useEffect(() => {
        loadUser();
    }, [loadUser]);

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-xl">Loading...</div>
            </div>
        );
    }

    return (
        <Router>
            <div className="min-h-screen bg-gray-50">
                {isAuthenticated && <Navbar />}
                <Routes>
                    <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/" />} />
                    <Route path="/register" element={!isAuthenticated ? <Register /> : <Navigate to="/" />} />

                    <Route path="/" element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" />} />
                    <Route path="/map" element={isAuthenticated ? <MapView /> : <Navigate to="/login" />} />
                    <Route path="/reports" element={isAuthenticated ? <ReportList /> : <Navigate to="/login" />} />
                    <Route path="/reports/new" element={isAuthenticated ? <ReportForm /> : <Navigate to="/login" />} />
                    <Route path="/reports/:id" element={isAuthenticated ? <ReportDetail /> : <Navigate to="/login" />} />
                    <Route path="/authority" element={isAuthenticated ? <AuthorityDashboard /> : <Navigate to="/login" />} />
                    <Route path="/analytics" element={isAuthenticated ? <WardAnalyticsView /> : <Navigate to="/login" />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
