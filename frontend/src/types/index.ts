export interface User {
    id: number;
    email: string;
    full_name: string;
    phone?: string;
    role: 'CITIZEN' | 'AUTHORITY' | 'ADMIN';
    is_verified: boolean;
    digilocker_verified: boolean;
}

export interface Report {
    id: number;
    user_id: number;
    title: string;
    description: string;
    latitude: number;
    longitude: number;
    address?: string;
    ward_id?: number;
    status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';
    severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    assigned_agency?: 'MCD' | 'PWD' | 'NDMC' | 'DDA' | 'OTHER';
    image_path?: string;
    resolution_image_path?: string;
    upvote_count: number;
    comment_count: number;
    created_at: string;
    updated_at?: string;
    resolved_at?: string;
}

export interface Comment {
    id: number;
    report_id: number;
    user_id: number;
    content: string;
    created_at: string;
}

export interface Ward {
    id: number;
    ward_number: string;
    ward_name: string;
    risk_score: number;
    elevation_avg?: number;
    slope_avg?: number;
    incident_density: number;
}

export interface WardAnalytics {
    ward: Ward;
    total_reports: number;
    open_reports: number;
    resolved_reports: number;
    avg_resolution_time_hours?: number;
}
