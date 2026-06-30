import Sidebar from './Sidebar';
import { BrainCircuit } from 'lucide-react';
import { Outlet } from 'react-router-dom';

export default function Layout() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      {/* Top Header */}
      <header className="bg-white border-b border-slate-200 shadow-sm h-16 flex items-center px-6 sticky top-0 z-50">
        <div className="flex items-center">
          <BrainCircuit className="h-8 w-8 text-primary-600" />
          <span className="ml-3 text-xl font-bold bg-gradient-to-r from-primary-700 to-primary-500 bg-clip-text text-transparent tracking-tight">
            AI Research Assistant
          </span>
        </div>
      </header>

      {/* Main Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar Component */}
        <Sidebar />
        
        {/* Main Content Container */}
        <main className="flex-1 overflow-y-auto p-8">
          <div className="max-w-6xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
