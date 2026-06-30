import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Sparkles } from 'lucide-react';
import { ResearchService } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

export default function NewResearch() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await ResearchService.runResearch(query);
      navigate(`/reports/${response.report_id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to generate research. Please try again.");
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto pt-20">
        <LoadingSpinner message="Agents are actively researching..." />
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto pt-10 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="text-center mb-10">
        <div className="inline-flex items-center justify-center p-3 bg-primary-50 rounded-2xl mb-4 text-primary-600">
          <Sparkles className="w-8 h-8" />
        </div>
        <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight">What would you like to explore?</h1>
        <p className="mt-4 text-lg text-slate-600">
          Enter a topic and our multi-agent system will automatically plan, search, fact-check, and write a comprehensive report.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="relative group">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <Search className="h-6 w-6 text-slate-400 group-focus-within:text-primary-500 transition-colors" />
        </div>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="block w-full pl-12 pr-32 py-5 text-lg border border-slate-200 rounded-2xl shadow-sm focus:ring-4 focus:ring-primary-500/20 focus:border-primary-500 outline-none transition-all placeholder:text-slate-400"
          placeholder="e.g., Explain Quantum Computing in simple terms..."
          required
        />
        <div className="absolute inset-y-2 right-2">
          <button
            type="submit"
            disabled={!query.trim()}
            className="h-full px-6 bg-primary-600 text-white font-medium rounded-xl hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Generate
          </button>
        </div>
      </form>

      {error && (
        <div className="mt-6 p-4 bg-rose-50 rounded-xl border border-rose-200 text-rose-700 text-center">
          {error}
        </div>
      )}
    </div>
  );
}
