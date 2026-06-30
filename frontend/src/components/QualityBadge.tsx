export default function QualityBadge({ score }: { score: number }) {
  const getBadgeColor = (s: number) => {
    if (s >= 8.5) return 'bg-emerald-100 text-emerald-800 border-emerald-200';
    if (s >= 7.0) return 'bg-amber-100 text-amber-800 border-amber-200';
    return 'bg-rose-100 text-rose-800 border-rose-200';
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getBadgeColor(score)}`}>
      Score: {score.toFixed(1)}/10
    </span>
  );
}
