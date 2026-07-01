import { ExternalLink } from 'lucide-react';

/**
 * Renders a numbered citation list in [N] Title – URL format.
 * Supports two input formats:
 *   1. Two-line blocks: "Title\nURL" separated by blank lines
 *   2. Already-formatted "[N] ..." lines
 */
export default function CitationList({ citations }: { citations: string }) {
  if (!citations) return null;

  // Parse the citations string into structured { title, url } entries
  const entries: { title: string; url: string }[] = [];

  // If citations already contain [N] markers, parse line-by-line
  if (/^\s*\[\d+\]/.test(citations.trim())) {
    citations.split('\n').forEach(line => {
      const trimmed = line.trim();
      if (!trimmed) return;
      // Strip leading [N] marker
      const withoutIndex = trimmed.replace(/^\[\d+\]\s*/, '');
      // Try to split on " – " or " - " to get title vs URL
      const dashIdx = withoutIndex.search(/\s[–-]\s/);
      if (dashIdx !== -1) {
        entries.push({
          title: withoutIndex.slice(0, dashIdx).trim(),
          url: withoutIndex.slice(dashIdx).replace(/^\s*[–-]\s*/, '').trim(),
        });
      } else {
        entries.push({ title: withoutIndex, url: '#' });
      }
    });
  } else {
    // Legacy two-line-block format: "Title\nURL\n\nTitle\nURL"
    citations.split('\n\n').forEach(block => {
      const lines = block.trim().split('\n');
      if (lines.length === 0 || !lines[0]) return;
      entries.push({
        title: lines[0].trim(),
        url: lines[1]?.trim() || '#',
      });
    });
  }

  if (entries.length === 0) return null;

  return (
    <div className="mt-10 bg-slate-50 p-6 rounded-xl border border-slate-200">
      <h3 className="text-base font-semibold text-slate-800 mb-4 uppercase tracking-wide text-xs">
        References
      </h3>
      <ol className="space-y-3">
        {entries.map((entry, i) => {
          const isUrl = entry.url !== '#' && (entry.url.startsWith('http') || entry.url.startsWith('www'));
          return (
            <li key={i} className="flex gap-3 items-start">
              <span className="shrink-0 w-6 h-6 flex items-center justify-center rounded-full bg-primary-100 text-primary-700 text-xs font-bold mt-0.5">
                {i + 1}
              </span>
              <div className="flex flex-col">
                <span className="font-medium text-slate-700 text-sm">{entry.title}</span>
                {isUrl ? (
                  <a
                    href={entry.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:text-primary-800 text-xs flex items-center mt-0.5 w-fit group transition-colors"
                  >
                    {entry.url}
                    <ExternalLink className="w-3 h-3 ml-1 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </a>
                ) : (
                  <span className="text-slate-400 text-xs mt-0.5">{entry.url !== '#' ? entry.url : ''}</span>
                )}
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
