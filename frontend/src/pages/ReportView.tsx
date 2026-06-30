import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { Download, Trash2, ArrowLeft, Calendar, FileText } from 'lucide-react';
import { ResearchService } from '../services/api';
import { Report } from '../types/report';
import QualityBadge from '../components/QualityBadge';
import CitationList from '../components/CitationList';

export default function ReportView() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const data = await ResearchService.getReport(Number(id));
        setReport(data);
      } catch (err) {
        setError("Failed to load report. It may have been deleted.");
      } finally {
        setLoading(false);
      }
    };
    if (id) fetchReport();
  }, [id]);

  const handleDownload = async () => {
    if (!id) return;
    setDownloading(true);
    try {
      await ResearchService.downloadPdf(Number(id));
    } catch (err) {
      console.error("Download failed", err);
      alert("Failed to download PDF.");
    } finally {
      setDownloading(false);
    }
  };

  const handleDelete = async () => {
    if (!id) return;
    const confirm = window.confirm("Are you sure you want to delete this report? This action cannot be undone.");
    if (!confirm) return;

    try {
      await ResearchService.deleteReport(Number(id));
      navigate('/history');
    } catch (err) {
      alert("Failed to delete report.");
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="text-center py-20">
        <h2 className="text-2xl font-bold text-slate-800 mb-4">{error || "Report not found"}</h2>
        <button onClick={() => navigate('/history')} className="text-primary-600 hover:underline">
          Return to History
        </button>
      </div>
    );
  }

  const dateStr = new Date(report.created_at).toLocaleString(undefined, {
    dateStyle: 'medium', timeStyle: 'short'
  });

  return (
    <div className="max-w-4xl mx-auto pb-20 animate-in fade-in duration-500">
      <button 
        onClick={() => navigate(-1)}
        className="inline-flex items-center text-sm font-medium text-slate-500 hover:text-slate-900 mb-8 transition-colors"
      >
        <ArrowLeft className="w-4 h-4 mr-1" />
        Back
      </button>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        {/* Header Metadata */}
        <div className="bg-slate-50 border-b border-slate-200 p-6 md:p-10">
          <div className="flex flex-wrap items-center gap-4 mb-4">
            <QualityBadge score={report.quality_score} />
            <span className="flex items-center text-slate-500 text-sm">
              <Calendar className="w-4 h-4 mr-1" />
              {dateStr}
            </span>
          </div>
          
          <h1 className="text-3xl md:text-4xl font-bold text-slate-900 leading-tight mb-6">
            {report.query}
          </h1>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={handleDownload}
              disabled={downloading}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none transition-colors disabled:opacity-50"
            >
              <Download className="w-4 h-4 mr-2" />
              {downloading ? "Generating PDF..." : "Export to PDF"}
            </button>
            <button
              onClick={handleDelete}
              className="inline-flex items-center px-4 py-2 border border-slate-200 rounded-lg shadow-sm text-sm font-medium text-rose-600 bg-white hover:bg-rose-50 hover:border-rose-300 focus:outline-none transition-colors"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Delete Report
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="p-6 md:p-10">
          <div className="markdown">
            <ReactMarkdown>{report.report}</ReactMarkdown>
          </div>

          {/* AI Review Feedback Box */}
          {report.review_feedback && (
            <div className="mt-12 bg-amber-50 rounded-xl border border-amber-200 p-6">
              <h3 className="text-amber-900 font-bold mb-2 flex items-center">
                <FileText className="w-5 h-5 mr-2" />
                Editorial Review Feedback
              </h3>
              <p className="text-amber-800 text-sm whitespace-pre-wrap">
                {report.review_feedback}
              </p>
            </div>
          )}

          {/* Citations block mapped from DB schema */}
          {report.citations && !report.report.includes("References") && (
            <CitationList citations={report.citations} />
          )}
        </div>
      </div>
    </div>
  );
}
