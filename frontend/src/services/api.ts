import axios from 'axios';
import { Report } from '../types/report';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});



export const ResearchService = {
  runResearch: async (query: string): Promise<{ report_id: number, report: string, quality_score: number }> => {
    const response = await api.post('/research', { query });
    return response.data;
  },
  getReports: async (skip: number = 0, limit: number = 100): Promise<Report[]> => {
    const response = await api.get(`/reports?skip=${skip}&limit=${limit}`);
    return response.data;
  },
  getReport: async (id: number): Promise<Report> => {
    const response = await api.get(`/reports/${id}`);
    return response.data;
  },
  deleteReport: async (id: number): Promise<void> => {
    await api.delete(`/reports/${id}`);
  },
  downloadPdf: async (id: number): Promise<void> => {
    const response = await api.get(`/reports/${id}/pdf`, { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `research_report_${id}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  }
};
