/**
 * Formats an ISO datetime string into the user's local timezone (falling back to Asia/Kolkata)
 * in the format: "Jul 1, 2026, 9:58 AM"
 */
export function formatReportDateTime(dateString: string | null | undefined): string {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return 'N/A';

  let timeZone = 'Asia/Kolkata';
  try {
    const resolved = Intl.DateTimeFormat().resolvedOptions().timeZone;
    if (resolved) {
      timeZone = resolved;
    }
  } catch (e) {
    // Fallback if resolvedOptions() fails
  }

  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
    timeZone: timeZone
  }).format(date);
}
