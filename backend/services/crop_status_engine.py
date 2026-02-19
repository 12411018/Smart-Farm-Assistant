"""Crop status calculation utilities."""

from datetime import datetime, timezone, date


def _as_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return None


def calculate_crop_status(plan, stages):
    """Compute status, current stage, and days passed for a crop plan."""
    today = datetime.now(timezone.utc).date()
    sowing_date = _as_date(plan.sowing_date) or today

    days_passed = (today - sowing_date).days

    if days_passed < 0:
        overall_status = "Not started"
    elif days_passed >= plan.growth_duration_days:
        overall_status = "Completed"
    else:
        overall_status = "In Progress"

    current_stage = "Not started"
    sorted_stages = sorted(
        (s for s in stages if _as_date(s.start_date) and _as_date(s.end_date)),
        key=lambda s: _as_date(s.start_date),
    )

    if sorted_stages:
        first_start = _as_date(sorted_stages[0].start_date)
        last_end = _as_date(sorted_stages[-1].end_date)

        for stage in sorted_stages:
            start = _as_date(stage.start_date)
            end = _as_date(stage.end_date)
            if start and end and start <= today <= end:
                current_stage = stage.stage
                break

        if today < first_start:
            current_stage = "Not started"
        elif today > last_end:
            current_stage = "Completed"

    progress = 0
    if plan.growth_duration_days:
        progress = max(0, min(100, round((days_passed / plan.growth_duration_days) * 100)))

    return {
        "days_passed": max(days_passed, 0),
        "overall_status": overall_status,
        "current_stage": current_stage,
        "progress": progress,
    }
