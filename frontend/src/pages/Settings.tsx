import { Bot, BookOpen, AlignLeft, Database, Clock } from 'lucide-react';

function ComingSoonBadge() {
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-semibold bg-violet-100 text-violet-700 rounded-full">
      <Clock className="w-3 h-3" />
      Coming Soon
    </span>
  );
}

export default function Settings() {
  return (
    <div className="animate-in fade-in duration-500 max-w-2xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Settings</h1>
        <p className="mt-2 text-slate-600">Manage your AI Research Assistant preferences.</p>
      </div>

      <div className="space-y-6">

        {/* LLM Provider */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="flex items-center gap-3 px-6 py-4 border-b border-slate-100 bg-slate-50">
            <Bot className="w-5 h-5 text-primary-600" />
            <h2 className="font-semibold text-slate-800">LLM Provider</h2>
          </div>
          <div className="px-6 py-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">Current Provider</p>
                <p className="text-lg font-bold text-slate-900 mt-0.5">Gemini</p>
              </div>
              <ComingSoonBadge />
            </div>
          </div>
        </div>

        {/* Research Settings */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="flex items-center gap-3 px-6 py-4 border-b border-slate-100 bg-slate-50">
            <BookOpen className="w-5 h-5 text-primary-600" />
            <h2 className="font-semibold text-slate-800">Research Settings</h2>
          </div>
          <ul className="divide-y divide-slate-100">
            <li className="flex items-center justify-between px-6 py-4">
              <div className="flex items-center gap-3">
                <Database className="w-4 h-4 text-slate-400" />
                <span className="text-slate-700 font-medium">Max Sources</span>
              </div>
              <ComingSoonBadge />
            </li>
            <li className="flex items-center justify-between px-6 py-4">
              <div className="flex items-center gap-3">
                <AlignLeft className="w-4 h-4 text-slate-400" />
                <span className="text-slate-700 font-medium">Citation Style</span>
              </div>
              <ComingSoonBadge />
            </li>
            <li className="flex items-center justify-between px-6 py-4">
              <div className="flex items-center gap-3">
                <BookOpen className="w-4 h-4 text-slate-400" />
                <span className="text-slate-700 font-medium">Report Length</span>
              </div>
              <ComingSoonBadge />
            </li>
          </ul>
        </div>

      </div>
    </div>
  );
}
