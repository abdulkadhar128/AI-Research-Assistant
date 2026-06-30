import { Settings as SettingsIcon } from 'lucide-react';

export default function Settings() {
  return (
    <div className="animate-in fade-in duration-500">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Settings</h1>
        <p className="mt-2 text-slate-600">Manage your AI Research Assistant preferences.</p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-12 text-center">
        <SettingsIcon className="w-12 h-12 text-slate-300 mx-auto mb-4 animate-[spin_4s_linear_infinite]" />
        <h3 className="text-lg font-medium text-slate-900 mb-2">Configuration Pending</h3>
        <p className="text-slate-500 max-w-md mx-auto">
          Settings integrations (e.g., LLM model switching, API key overrides, and theme preferences) will be implemented here.
        </p>
      </div>
    </div>
  );
}
