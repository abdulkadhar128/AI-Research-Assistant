import { Loader2 } from 'lucide-react';

export default function LoadingSpinner({ message = "Generating Research..." }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 bg-white rounded-xl shadow-sm border border-slate-100">
      <Loader2 className="w-12 h-12 text-primary-500 animate-spin mb-4" />
      <p className="text-slate-600 font-medium text-lg animate-pulse">{message}</p>
      <p className="text-slate-400 text-sm mt-2 text-center max-w-sm">
        Our multi-agent system is currently searching, reading, analyzing, and synthesizing information. This may take a minute.
      </p>
    </div>
  );
}
