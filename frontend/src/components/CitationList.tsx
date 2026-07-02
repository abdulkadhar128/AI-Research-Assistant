import { ExternalLink, BookOpen } from 'lucide-react';

/**
 * Renders a numbered citation list.
 * Expected input format (one per line): [N] Title — URL
 */
export default function CitationList({ citations }: { citations: string }) {
  if (!citations?.trim()) return null;

  // Parse each non-empty line as "[N] Title — URL"
  const entries: { index: number; title: string; url: string }[] = [];

  citations.split('\n').forEach(line => {
    const trimmed = line.trim();
    if (!trimmed) return;

    // Match "[N] ..." prefix
    const indexMatch = trimmed.match(/^\[(\d+)\]\s*/);
    const index = indexMatch ? parseInt(indexMatch[1], 10) : entries.length + 1;
    const rest  = indexMatch ? trimmed.slice(indexMatch[0].length) : trimmed;

    // Split on " — " or " - " to separate title from URL
    const separatorIdx = rest.search(/\s[—–-]\s/);
    if (separatorIdx !== -1) {
      const title = rest.slice(0, separatorIdx).trim();
      const url   = rest.slice(separatorIdx).replace(/^\s*[—–-]\s*/, '').trim();
      entries.push({ index, title, url });
    } else {
      // Whole line is either a URL or a title with no URL
      const isUrl = /^https?:\/\//.test(rest);
      entries.push({ index, title: isUrl ? rest : rest, url: isUrl ? rest : '' });
    }
  });

  if (entries.length === 0) return null;

  return (
    <div className="mt-10 bg-slate-50 p-6 rounded-xl border border-slate-200">
      <h3 className="flex items-center gap-2 text-xs font-semibold text-slate-500 uppercase tracking-widest mb-5">
        <BookOpen className="w-4 h-4" />
        References
      </h3>
      <ol className="space-y-4">
        {entries.map((entry) => {
          const isValidUrl = entry.url.startsWith('http');
          return (
            <li key={entry.index} className="flex gap-3 items-start">
              <span className="shrink-0 w-6 h-6 flex items-center justify-center rounded-full bg-primary-100 text-primary-700 text-xs font-bold mt-0.5">
                {entry.index}
              </span>
              <div className="flex flex-col min-w-0">
                <span className="font-medium text-slate-800 text-sm leading-snug">
                  {entry.title}
                </span>
                {isValidUrl ? (
                  <a
                    href={entry.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:text-primary-800 text-xs flex items-center gap-1 mt-0.5 w-fit group transition-colors truncate max-w-full"
                    title={entry.url}
                  >
                    <span className="truncate">{entry.url}</span>
                    <ExternalLink className="w-3 h-3 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </a>
                ) : entry.url ? (
                  <span className="text-slate-400 text-xs mt-0.5">{entry.url}</span>
                ) : null}
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}

