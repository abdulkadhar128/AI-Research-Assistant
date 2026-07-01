import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FileText, Star, CalendarDays, Plus, Timer } from 'lucide-react';
import { ResearchService } from '../services/api';
import { Report } from '../types/report';

export default function Dashboard() {
  const [recentReports, setRecentReports] = useState<Report[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [avgScore, setAvgScore] = useState(0);
  const [weekCount, setWeekCount] = useState(0);
  const [avgGenTime, setAvgGenTime] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await ResearchService.getReports(0, 50);
        setTotalCount(data.length);
        if (data.length > 0) {
          const sum = data.reduce((acc, r) => acc + r.quality_score, 0);
          setAvgScore(sum / data.length);
          const oneWeekAgo = new Date();
          oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
          setWeekCount(data.filter(r => new Date(r.created_at) >= oneWeekAgo).length);
          const timed = data.filter(r => r.generation_time != null);
          if (timed.length > 0) {
            const tSum = timed.reduce((acc, r) => acc + (r.generation_time ?? 0), 0);
            setAvgGenTime(tSum / timed.length);
          }
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

      {/* Stats Board */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-primary-50 rounded-xl">
            <FileText className="w-6 h-6 text-primary-600" />
          </div>
          <div>
            <p className="text-slate-500 text-sm font-medium">Total Reports</p>
            <p className="text-3xl font-extrabold text-slate-900">{loading ? '-' : totalCount}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-emerald-50 rounded-xl">
            <Star className="w-6 h-6 text-emerald-600" />
          </div>
          <div>
            <p className="text-slate-500 text-sm font-medium">Average Quality Score</p>
            <p className="text-3xl font-extrabold text-slate-900">{loading ? '-' : avgScore.toFixed(1)}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-violet-50 rounded-xl">
            <CalendarDays className="w-6 h-6 text-violet-600" />
          </div>
          <div>
            <p className="text-slate-500 text-sm font-medium">Reports This Week</p>
            <p className="text-3xl font-extrabold text-slate-900">{loading ? '-' : weekCount}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-amber-50 rounded-xl">
            <Timer className="w-6 h-6 text-amber-600" />
          </div>
          <div>
            <p className="text-slate-500 text-sm font-medium">Avg Generation Time</p>
            <p className="text-3xl font-extrabold text-slate-900">
              {loading ? '-' : avgGenTime != null ? `${avgGenTime.toFixed(0)}s` : 'N/A'}
            </p>
          </div>
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
          <div className="bg-white rounded-xl border border-slate-200 border-dashed p-12 text-center">
            <div className="inline-flex items-center justify-center p-3 bg-primary-50 rounded-2xl mb-4">
              <FileText className="w-8 h-8 text-primary-500" />
            </div>
            <p className="text-slate-700 font-semibold text-lg mb-1">No reports generated yet.</p>
            <p className="text-slate-500 text-sm mb-6">Start by asking a question and let our AI agents do the research.</p>
            <button
              onClick={() => navigate('/new')}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary-600 text-white font-medium rounded-xl hover:bg-primary-700 transition-colors shadow-sm"
            >
              <Plus className="w-4 h-4" />
              Generate Your First Report
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
