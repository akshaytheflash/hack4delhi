import axios from 'axios';
import { User, Report, Comment, Ward, WardAnalytics } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://hack4delhi-zc9t.onrender.com';

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000, // 10 seconds timeout
    headers: {
        'Content-Type': 'application/json',
    },
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export const authAPI = {
    register: (data: { email: string; password: string; full_name: string; phone?: string; role: string }) =>
        api.post<User>('/auth/register', data),

    login: (email: string, password: string) =>
        api.post<{ access_token: string; refresh_token: string }>('/auth/login', { email, password }),

    getCurrentUser: () =>
        api.get<User>('/auth/me'),
};

export const reportsAPI = {
    create: (formData: FormData) =>
        api.post<Report>('/reports/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        }),

    getAll: (params?: { skip?: number; limit?: number; status?: string; ward_id?: number; severity?: string }) =>
        api.get<{ reports: Report[]; total: number; page: number; page_size: number }>('/reports/', { params }),

    getById: (id: number) =>
        api.get<Report>(`/reports/${id}`),

    upvote: (id: number) =>
        api.post(`/reports/${id}/upvote`),

    addComment: (id: number, content: string) =>
        api.post<Comment>(`/reports/${id}/comments`, { content }),

    getComments: (id: number) =>
        api.get<Comment[]>(`/reports/${id}/comments`),
};

export const authorityAPI = {
    updateReport: (id: number, data: { status?: string; severity?: string; assigned_agency?: string; notes?: string }) =>
        api.put<Report>(`/authority/reports/${id}`, data),

    uploadResolutionImage: (id: number, file: File) => {
        const formData = new FormData();
        formData.append('image', file);
        return api.post(`/authority/reports/${id}/resolution-image`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
    },

    getAuditLog: (id: number) =>
        api.get(`/authority/reports/${id}/audit-log`),
};

export const analyticsAPI = {
    getWards: () =>
        api.get<Ward[]>('/analytics/wards'),

    getWardAnalytics: (id: number) =>
        api.get<WardAnalytics>(`/analytics/wards/${id}`),

    getHotspots: () =>
        api.get('/analytics/hotspots'),

    getReportsGeoJSON: (status?: string) =>
        api.get('/analytics/reports-geojson', { params: { status } }),
};

export default api;
