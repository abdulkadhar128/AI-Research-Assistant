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
  runResearch: async (query: string, onProgress?: (status: string) => void): Promise<any> => {
    const response = await fetch(`${API_URL}/research`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ query })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to generate research');
    }

    if (!response.body) {
      throw new Error('ReadableStream not yet supported in this browser.');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    let finalData = null;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || ''; // keep incomplete chunk in buffer

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.substring(6).trim();
          try {
            const data = JSON.parse(dataStr);
            if (data.status === 'complete') {
              finalData = data.data;
            } else if (data.status === 'error') {
              throw new Error(data.detail || 'Workflow error');
            } else if (onProgress && data.status) {
              onProgress(data.status);
            }
          } catch (e) {
            console.error("Failed to parse SSE chunk:", dataStr);
          }
        }
      }
    }

    if (!finalData) {
      throw new Error("Stream ended without completing");
    }

    return finalData;
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
