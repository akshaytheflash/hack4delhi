import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { reportsAPI } from '../../services/api';
import { Report, Comment } from '../../types';

export default function ReportDetail() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [report, setReport] = useState<Report | null>(null);
    const [comments, setComments] = useState<Comment[]>([]);
    const [newComment, setNewComment] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (id) {
            loadReport();
            loadComments();
        }
    }, [id]);

    const loadReport = async () => {
        try {
            const response = await reportsAPI.getById(Number(id));
            setReport(response.data);
        } catch (error) {
            console.error('Error loading report:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadComments = async () => {
        try {
            const response = await reportsAPI.getComments(Number(id));
            setComments(response.data);
        } catch (error) {
            console.error('Error loading comments:', error);
        }
    };

    const handleUpvote = async () => {
        try {
            await reportsAPI.upvote(Number(id));
            loadReport();
        } catch (error: any) {
            alert(error.response?.data?.detail || 'Failed to upvote');
        }
    };

    const handleAddComment = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newComment.trim()) return;

        try {
            await reportsAPI.addComment(Number(id), newComment);
            setNewComment('');
            loadComments();
            loadReport();
        } catch (error: any) {
            alert(error.response?.data?.detail || 'Failed to add comment');
        }
    };

    if (loading) {
        return <div className="text-center py-12">Loading...</div>;
    }

    if (!report) {
        return <div className="text-center py-12">Report not found</div>;
    }

    return (
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <button
                onClick={() => navigate('/reports')}
                className="mb-4 text-primary-600 hover:text-primary-700"
            >
                ← Back to Reports
            </button>

            <div className="bg-white shadow-md rounded-lg p-6 mb-6">
                <div className="flex justify-between items-start mb-4">
                    <h1 className="text-3xl font-bold text-gray-900">{report.title}</h1>
                    <div className="flex space-x-2">
                        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${report.status === 'OPEN' ? 'bg-red-100 text-red-800' :
                            report.status === 'IN_PROGRESS' ? 'bg-yellow-100 text-yellow-800' :
                                report.status === 'RESOLVED' ? 'bg-green-100 text-green-800' :
                                    'bg-gray-100 text-gray-800'
                            }`}>
                            {report.status}
                        </span>
                        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${report.severity === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                            report.severity === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                                report.severity === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                                    'bg-green-100 text-green-800'
                            }`}>
                            {report.severity}
                        </span>
                    </div>
                </div>

                <p className="text-gray-700 mb-6">{report.description}</p>

                <div className="grid grid-cols-2 gap-4 mb-6 text-sm">
                    <div>
                        <span className="font-semibold">Location:</span>{' '}
                        {report.address || `${report.latitude.toFixed(6)}, ${report.longitude.toFixed(6)}`}
                    </div>
                    <div>
                        <span className="font-semibold">Reported:</span>{' '}
                        {new Date(report.created_at).toLocaleString()}
                    </div>
                    {report.assigned_agency && (
                        <div>
                            <span className="font-semibold">Assigned to:</span> {report.assigned_agency}
                        </div>
                    )}
                    {report.resolved_at && (
                        <div>
                            <span className="font-semibold">Resolved:</span>{' '}
                            {new Date(report.resolved_at).toLocaleString()}
                        </div>
                    )}
                </div>

                {report.image_path && (
                    <div className="mb-6">
                        <h3 className="font-semibold mb-2">Photo:</h3>
                        <img
                            src={`/api/${report.image_path}`}
                            alt="Report"
                            className="max-w-full h-auto rounded-lg"
                        />
                    </div>
                )}

                {report.resolution_image_path && (
                    <div className="mb-6">
                        <h3 className="font-semibold mb-2">Resolution Photo:</h3>
                        <img
                            src={`/api/${report.resolution_image_path}`}
                            alt="Resolution"
                            className="max-w-full h-auto rounded-lg"
                        />
                    </div>
                )}

                <div className="flex items-center space-x-4">
                    <button
                        onClick={handleUpvote}
                        className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700"
                    >
                        👍 Upvote ({report.upvote_count})
                    </button>
                </div>
            </div>

            <div className="bg-white shadow-md rounded-lg p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">
                    Comments ({report.comment_count})
                </h2>

                <form onSubmit={handleAddComment} className="mb-6">
                    <textarea
                        value={newComment}
                        onChange={(e) => setNewComment(e.target.value)}
                        placeholder="Add a comment..."
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                    <button
                        type="submit"
                        className="mt-2 bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700"
                    >
                        Post Comment
                    </button>
                </form>

                <div className="space-y-4">
                    {comments.map((comment) => (
                        <div key={comment.id} className="border-l-4 border-primary-200 pl-4 py-2">
                            <p className="text-gray-700">{comment.content}</p>
                            <p className="text-sm text-gray-500 mt-1">
                                {new Date(comment.created_at).toLocaleString()}
                            </p>
                        </div>
                    ))}
                </div>

                {comments.length === 0 && (
                    <p className="text-gray-500 text-center py-4">No comments yet. Be the first to comment!</p>
                )}
            </div>
        </div>
    );
}
