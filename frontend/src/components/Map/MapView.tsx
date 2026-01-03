import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, GeoJSON } from 'react-leaflet';
import { LatLngExpression } from 'leaflet';
import L from 'leaflet';
import { analyticsAPI } from '../../services/api';

import 'leaflet/dist/leaflet.css';

const defaultCenter: LatLngExpression = [28.6139, 77.2090];

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const getSeverityColor = (severity: string) => {
    switch (severity) {
        case 'CRITICAL': return '#dc2626';
        case 'HIGH': return '#ea580c';
        case 'MEDIUM': return '#f59e0b';
        case 'LOW': return '#10b981';
        default: return '#6b7280';
    }
};

const getStatusColor = (status: string) => {
    switch (status) {
        case 'OPEN': return '#dc2626';
        case 'IN_PROGRESS': return '#f59e0b';
        case 'RESOLVED': return '#10b981';
        case 'CLOSED': return '#6b7280';
        default: return '#6b7280';
    }
};

export default function MapView() {
    const [reportsGeoJSON, setReportsGeoJSON] = useState<any>(null);
    const [hotspotsGeoJSON, setHotspotsGeoJSON] = useState<any>(null);
    const [showHotspots, setShowHotspots] = useState(true);
    const [statusFilter, setStatusFilter] = useState<string>('');

    useEffect(() => {
        loadMapData();
    }, [statusFilter]);

    const loadMapData = async () => {
        try {
            const [reportsRes, hotspotsRes] = await Promise.all([
                analyticsAPI.getReportsGeoJSON(statusFilter || undefined),
                analyticsAPI.getHotspots(),
            ]);
            setReportsGeoJSON(reportsRes.data);
            setHotspotsGeoJSON(hotspotsRes.data);
        } catch (error) {
            console.error('Error loading map data:', error);
        }
    };

    const getRiskColor = (riskScore: number) => {
        if (riskScore >= 75) return '#dc2626';
        if (riskScore >= 50) return '#ea580c';
        if (riskScore >= 25) return '#f59e0b';
        return '#10b981';
    };

    const wardStyle = (feature: any) => {
        const riskScore = feature.properties.risk_score || 0;
        return {
            fillColor: getRiskColor(riskScore),
            weight: 2,
            opacity: 1,
            color: 'white',
            fillOpacity: 0.3,
        };
    };

    return (
        <div className="h-screen flex flex-col">
            <div className="bg-white shadow-sm p-4">
                <div className="max-w-7xl mx-auto flex items-center justify-between">
                    <h1 className="text-2xl font-bold text-gray-900">Interactive Map</h1>
                    <div className="flex items-center space-x-4">
                        <label className="flex items-center">
                            <input
                                type="checkbox"
                                checked={showHotspots}
                                onChange={(e) => setShowHotspots(e.target.checked)}
                                className="mr-2"
                            />
                            <span className="text-sm">Show Hotspots</span>
                        </label>
                        <select
                            value={statusFilter}
                            onChange={(e) => setStatusFilter(e.target.value)}
                            className="px-3 py-1 border border-gray-300 rounded-md text-sm"
                        >
                            <option value="">All Reports</option>
                            <option value="OPEN">Open</option>
                            <option value="IN_PROGRESS">In Progress</option>
                            <option value="RESOLVED">Resolved</option>
                            <option value="CLOSED">Closed</option>
                        </select>
                    </div>
                </div>
            </div>

            <div className="flex-1">
                <MapContainer
                    center={defaultCenter}
                    zoom={11}
                    style={{ height: '100%', width: '100%' }}
                >
                    <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />

                    {showHotspots && hotspotsGeoJSON && (
                        <GeoJSON
                            data={hotspotsGeoJSON}
                            style={wardStyle}
                            onEachFeature={(feature, layer) => {
                                layer.bindPopup(`
                  <div>
                    <h3 class="font-bold">${feature.properties.ward_name}</h3>
                    <p>Ward: ${feature.properties.ward_number}</p>
                    <p>Risk Score: ${feature.properties.risk_score?.toFixed(1)}</p>
                    <p>Category: ${feature.properties.risk_category}</p>
                  </div>
                `);
                            }}
                        />
                    )}

                    {reportsGeoJSON?.features?.map((feature: any) => {
                        const [lng, lat] = feature.geometry.coordinates;
                        const props = feature.properties;

                        return (
                            <Marker key={feature.properties.id} position={[lat, lng]}>
                                <Popup>
                                    <div className="min-w-[200px]">
                                        <h3 className="font-bold text-lg mb-2">{props.title}</h3>
                                        <div className="space-y-1 text-sm">
                                            <p>
                                                <span className="font-semibold">Status:</span>{' '}
                                                <span style={{ color: getStatusColor(props.status) }}>
                                                    {props.status}
                                                </span>
                                            </p>
                                            <p>
                                                <span className="font-semibold">Severity:</span>{' '}
                                                <span style={{ color: getSeverityColor(props.severity) }}>
                                                    {props.severity}
                                                </span>
                                            </p>
                                            <p>
                                                <span className="font-semibold">Upvotes:</span> {props.upvote_count}
                                            </p>
                                            <p className="text-gray-500">
                                                {new Date(props.created_at).toLocaleDateString()}
                                            </p>
                                            <a
                                                href={`/reports/${props.id}`}
                                                className="text-primary-600 hover:text-primary-700 font-medium"
                                            >
                                                View Details →
                                            </a>
                                        </div>
                                    </div>
                                </Popup>
                            </Marker>
                        );
                    })}
                </MapContainer>
            </div>

            <div className="bg-white border-t p-4">
                <div className="max-w-7xl mx-auto flex items-center justify-between text-sm">
                    <div className="flex items-center space-x-6">
                        <div className="flex items-center">
                            <div className="w-4 h-4 bg-red-600 mr-2"></div>
                            <span>Critical/High Risk</span>
                        </div>
                        <div className="flex items-center">
                            <div className="w-4 h-4 bg-orange-600 mr-2"></div>
                            <span>Medium Risk</span>
                        </div>
                        <div className="flex items-center">
                            <div className="w-4 h-4 bg-green-600 mr-2"></div>
                            <span>Low Risk</span>
                        </div>
                    </div>
                    <div className="text-gray-600">
                        Total Reports: {reportsGeoJSON?.features?.length || 0}
                    </div>
                </div>
            </div>
        </div>
    );
}
