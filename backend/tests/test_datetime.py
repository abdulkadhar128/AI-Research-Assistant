from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.connection import Base
from backend.database.models import Report
from backend.utils.datetime_utils import (
    get_kolkata_timezone,
    convert_to_local_tz,
    format_local_datetime
)

def test_kolkata_timezone():
    tz = get_kolkata_timezone()
    # Kolkata is UTC+5:30
    assert tz is not None
    dt = datetime(2026, 7, 1, 10, 0, 0, tzinfo=timezone.utc)
    local_dt = dt.astimezone(tz)
    assert local_dt.utcoffset() == timedelta(hours=5, minutes=30)

def test_format_local_datetime():
    # Test AM formatting (9:58 AM IST is 4:28 AM UTC)
    dt = datetime(2026, 7, 1, 4, 28, 0, tzinfo=timezone.utc)
    formatted = format_local_datetime(dt)
    assert formatted == "Jul 1, 2026, 9:58 AM"
    
    # Test PM formatting (3:30 PM IST is 10:00 AM UTC)
    dt_pm = datetime(2026, 7, 1, 10, 0, 0, tzinfo=timezone.utc)
    formatted_pm = format_local_datetime(dt_pm)
    assert formatted_pm == "Jul 1, 2026, 3:30 PM"

def test_db_utc_datetime_decorator():
    # Setup in-memory sqlite db
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create a report with an explicit timezone-aware UTC datetime
        aware_dt = datetime(2026, 7, 1, 12, 0, 0, tzinfo=timezone.utc)
        report_aware = Report(
            query="Aware query",
            report="Content",
            quality_score=9.0,
            review_feedback="Good",
            created_at=aware_dt
        )
        session.add(report_aware)
        session.commit()

        # Retrieve and verify it is timezone aware and correct
        queried = session.query(Report).filter(Report.query == "Aware query").first()
        assert queried.created_at is not None
        assert queried.created_at.tzinfo == timezone.utc
        assert queried.created_at.hour == 12

        # Create a report with a naive datetime
        naive_dt = datetime(2026, 7, 1, 12, 0, 0)
        report_naive = Report(
            query="Naive query",
            report="Content",
            quality_score=8.0,
            review_feedback="Okay",
            created_at=naive_dt
        )
        session.add(report_naive)
        session.commit()

        # Retrieve and verify it was converted to timezone-aware UTC
        queried_naive = session.query(Report).filter(Report.query == "Naive query").first()
        assert queried_naive.created_at is not None
        assert queried_naive.created_at.tzinfo == timezone.utc
        assert queried_naive.created_at.hour == 12

        # Create a report relying on default (should be timezone-aware UTC)
        report_default = Report(
            query="Default query",
            report="Content",
            quality_score=7.0,
            review_feedback="Default",
        )
        session.add(report_default)
        session.commit()

        queried_default = session.query(Report).filter(Report.query == "Default query").first()
        assert queried_default.created_at is not None
        assert queried_default.created_at.tzinfo == timezone.utc

    finally:
        session.close()
