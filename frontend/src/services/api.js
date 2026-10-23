import axios from 'axios';
const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000', timeout: 90000 });
api.interceptors.response.use(r=>r, error=>{ const detail=error?.response?.data?.detail; error.userMessage=typeof detail==='string'?detail:(error.message || 'Something went wrong. Please try again.'); return Promise.reject(error); });
export default api;
