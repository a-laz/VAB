import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export const createInterviewSession = async (jobRole: string, interviewType: string) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/api/interview-sessions/create/`, {
            job_role: jobRole,
            interview_type: interviewType,
            duration_minutes: 15  // Default value
        });
        return response.data.session_id;
    } catch (error) {
        console.error('Failed to create interview session:', error);
        throw error;
    }
}; 