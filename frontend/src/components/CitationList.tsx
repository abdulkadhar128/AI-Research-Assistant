import { ExternalLink } from 'lucide-react';

export default function CitationList({ citations }: { citations: string }) {
  if (!citations) return null;

  const blocks = citations.split('\n\n').filter(b => b.trim() !== '');

  return (
    <div className="bg-slate-50 p-6 rounded-xl border border-slate-200 mt-8">
      <h3 className="text-lg font-semibold text-slate-800 mb-4">Verified Sources</h3>
      <ul className="space-y-4">
        {blocks.map((block, i) => {
          const lines = block.split('\n');
          const title = lines[0] || `Source ${i + 1}`;
          const url = lines[1] || '#';
          
          return (
            <li key={i} className="flex flex-col">
              <span className="font-medium text-slate-700">{title}</span>
              <a 
                href={url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-primary-600 hover:text-primary-800 text-sm flex items-center mt-1 w-fit group transition-colors"
              >
                {url}
                <ExternalLink className="w-3 h-3 ml-1 opacity-0 group-hover:opacity-100 transition-opacity" />
              </a>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
