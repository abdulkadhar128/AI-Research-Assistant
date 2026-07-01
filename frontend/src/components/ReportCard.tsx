import { Link } from 'react-router-dom';
import { ArrowRight, FileText, Calendar } from 'lucide-react';
import { Report } from '../types/report';
import QualityBadge from './QualityBadge';
import { formatReportDateTime } from '../utils/date';

export default function ReportCard({ report }: { report: Report }) {
  const dateStr = formatReportDateTime(report.created_at);

  return (
    <Link 
      to={`/reports/${report.id}`}
      className="group block bg-white rounded-xl shadow-sm hover:shadow-md border border-slate-200 hover:border-primary-200 transition-all duration-200 overflow-hidden flex flex-col h-full"
    >
      <div className="p-6 flex flex-col flex-grow">
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center text-slate-500 text-xs">
            <Calendar className="w-4 h-4 mr-2" />
            {dateStr}
          </div>
          <QualityBadge score={report.quality_score} />
        </div>
        
        <h3 className="text-lg font-bold text-slate-900 mb-2 line-clamp-2 group-hover:text-primary-600 transition-colors">
          {report.query}
        </h3>
        
        <p className="text-slate-500 text-sm line-clamp-3 mb-6 flex-grow">
          {report.report.replace(/[#*`]/g, '').substring(0, 150)}...
        </p>

        <div className="flex items-center text-primary-600 font-medium text-sm mt-auto pt-4 border-t border-slate-50">
          <FileText className="w-4 h-4 mr-2" />
          View Full Report
          <ArrowRight className="w-4 h-4 ml-1 transform group-hover:translate-x-1 transition-transform" />
        </div>
      </div>
    </Link>
  );
}
