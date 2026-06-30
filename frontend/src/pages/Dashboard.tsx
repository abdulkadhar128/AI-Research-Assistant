import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ResearchService } from '../services/api';
import { Report } from '../types/report';

export default function Dashboard() {
  const [recentReports, setRecentReports] = useState<Report[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [avgScore, setAvgScore] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await ResearchService.getReports(0, 50);
        setTotalCount(data.length);
        if (data.length > 0) {
          const sum = data.reduce((acc, r) => acc + r.quality_score, 0);
          setAvgScore(sum / data.length);
        }
        setRecentReports(data.slice(0, 5)); // Show top 5
      } catch (err) {
        console.error("Failed to fetch reports:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Dashboard</h1>
      </div>

      {/* Stats Board matching mockup */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col justify-center">
          <p className="text-slate-500 font-medium mb-1">Total Reports</p>
          <p className="text-4xl font-extrabold text-primary-600">{loading ? '-' : totalCount}</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col justify-center">
          <p className="text-slate-500 font-medium mb-1">Avg Score</p>
          <p className="text-4xl font-extrabold text-emerald-600">{loading ? '-' : avgScore.toFixed(1)}</p>
        </div>
      </div>

      {/* Recent Reports List matching mockup */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 mb-4 border-b border-slate-200 pb-2">Recent Reports</h2>
        
        {loading ? (
          <div className="text-slate-400">Loading recent reports...</div>
        ) : recentReports.length > 0 ? (
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <ul className="divide-y divide-slate-100">
              {recentReports.map((report) => (
                <li key={report.id}>
                  <Link 
                    to={`/reports/${report.id}`} 
                    className="flex items-center justify-between p-4 hover:bg-slate-50 transition-colors group"
                  >
                    <span className="font-medium text-slate-700 group-hover:text-primary-600 transition-colors line-clamp-1 pr-4">
                      {report.query}
                    </span>
                    <span className="font-semibold text-slate-900 shrink-0">
                      {report.quality_score.toFixed(1)}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <p className="text-slate-500 bg-white p-6 rounded-xl border border-slate-200">No reports generated yet.</p>
        )}
      </div>
    </div>
  );
}
