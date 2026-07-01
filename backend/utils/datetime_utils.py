from datetime import datetime, timezone, timedelta
import zoneinfo

def get_kolkata_timezone():
    """
    Get the Asia/Kolkata timezone object. 
    Falls back to a fixed UTC+5:30 offset if zoneinfo database is not available 
    (e.g., on Windows without the tzdata package).
    """
    try:
        return zoneinfo.ZoneInfo("Asia/Kolkata")
    except Exception:
        # Fallback to fixed UTC+5:30 offset (IST)
        return timezone(timedelta(hours=5, minutes=30), name="IST")

def convert_to_local_tz(dt: datetime, tz=None) -> datetime:
    """
    Convert a timezone-aware datetime to a target timezone (defaults to Asia/Kolkata).
    If naive, first localize it to UTC.
    """
    if dt is None:
        return None
    if tz is None:
        tz = get_kolkata_timezone()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz)

def format_local_datetime(dt: datetime) -> str:
    """
    Format datetime into the user's local timezone (Asia/Kolkata) with the format:
    Jul 1, 2026, 9:58 AM
    """
    if dt is None:
        return "N/A"
    
    local_dt = convert_to_local_tz(dt)
    
    month = local_dt.strftime("%b")
    day = local_dt.day
    year = local_dt.year
    hour = int(local_dt.strftime("%I"))  # hour without leading zero
    minute = local_dt.strftime("%M")
    am_pm = local_dt.strftime("%p")
    
    return f"{month} {day}, {year}, {hour}:{minute} {am_pm}"
