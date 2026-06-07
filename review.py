import os
import sys
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'journal', 'templates')
OUTPUT_DIR   = os.path.join(BASE_DIR, 'journal')


# ---------------------------------------------------------------------------
# Shared week math  (mirrors sort.py exactly)
# ---------------------------------------------------------------------------

def week_saturday(dt):
    """Return the Saturday that closes the Sun–Sat week containing dt."""
    days_ahead = (5 - dt.weekday()) % 7
    return (dt + timedelta(days=days_ahead)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

def week_sunday(saturday):
    """Return the Sunday that opens the week whose Saturday is given."""
    return saturday - timedelta(days=6)

def week_number(saturday):
    """
    1-based week number for the week whose closing Saturday is given.
    Week 1 = the week whose Saturday first falls in the year.
    """
    year     = saturday.year
    jan1     = datetime(year, 1, 1)
    first_sat = jan1 + timedelta(days=(5 - jan1.weekday()) % 7)
    delta    = (saturday - first_sat).days
    return delta // 7 + 1


# ---------------------------------------------------------------------------
# "Which period am I reviewing?" logic
#
# Weekly:   always the last *completed* week (the one that ended last Saturday).
#           Running on Sunday means last Saturday was yesterday — correct.
#
# Monthly:  if today's date is past the midpoint of the month → current month.
#           Otherwise → previous month.
#
# Quarterly: if we are past the midpoint of the current quarter → current quarter.
#            Otherwise → previous quarter.
#
# Yearly:   if we are past July 1 (past halfway) → current year.
#           Otherwise → previous year.
#
# Triannual: same halfway logic over a 3-year cycle.
# ---------------------------------------------------------------------------

def target_week(now=None):
    """
    Return the Saturday of the last completed Sun–Sat week.
    'Completed' means the Saturday has already passed relative to now.
    On a Sunday, that is yesterday.
    """
    now = now or datetime.now()
    # Most recent Saturday on or before yesterday
    yesterday = now - timedelta(days=1)
    sat = week_saturday(yesterday)
    # If week_saturday(yesterday) is in the future relative to yesterday, step back a week
    if sat > yesterday:
        sat -= timedelta(weeks=1)
    sun  = week_sunday(sat)
    wnum = week_number(sat)
    print(f"[review] Target week: {sun.strftime('%m-%d-%Y')} – {sat.strftime('%m-%d-%Y')}  (week {wnum:02d})")
    return sat


def target_month(now=None):
    """
    Return (year, month) for the month to review.
    If today is past the midpoint of the current month → current month.
    Otherwise → previous month.
    """
    now = now or datetime.now()
    # Midpoint: day 15 is a reasonable halfway marker for any month
    if now.day >= 15:
        year, month = now.year, now.month
        reason = "past midpoint of current month"
    else:
        # Step back one month
        if now.month == 1:
            year, month = now.year - 1, 12
        else:
            year, month = now.year, now.month - 1
        reason = "before midpoint — using previous month"
    print(f"[review] Target month: {datetime(year, month, 1).strftime('%B %Y')}  ({reason})")
    return year, month


def target_quarter(now=None):
    """
    Return (year, quarter) for the quarter to review.
    If today is past the midpoint of the current quarter → current quarter.
    Otherwise → previous quarter.
    Quarter midpoints: Q1→Feb 15, Q2→May 15, Q3→Aug 15, Q4→Nov 15.
    """
    now     = now or datetime.now()
    q       = (now.month - 1) // 3 + 1
    q_start = datetime(now.year, (q - 1) * 3 + 1, 1)
    # Midpoint is 45 days into the quarter (roughly)
    q_mid   = q_start + timedelta(days=45)

    if now >= q_mid:
        year, quarter = now.year, q
        reason = "past midpoint of current quarter"
    else:
        if q == 1:
            year, quarter = now.year - 1, 4
        else:
            year, quarter = now.year, q - 1
        reason = "before midpoint — using previous quarter"

    print(f"[review] Target quarter: Q{quarter} {year}  ({reason})")
    return year, quarter


def target_year(now=None):
    """
    Return the year to review.
    If today is past July 1 (past halfway) → current year.
    Otherwise → previous year.
    """
    now = now or datetime.now()
    if now >= datetime(now.year, 7, 1):
        year   = now.year
        reason = "past midpoint of current year"
    else:
        year   = now.year - 1
        reason = "before midpoint — using previous year"
    print(f"[review] Target year: {year}  ({reason})")
    return year


def target_tri_year(now=None):
    """
    Return (tri_start, tri_end) for the 3-year cycle to review.
    Cycles: …2022-2024, 2025-2027, 2028-2030…
    Midpoint = 18 months into the cycle.
    """
    now          = now or datetime.now()
    cycle_start  = now.year - (now.year % 3)   # e.g. 2025 → 2025 (2025%3==0 → 0)
    mid_date     = datetime(cycle_start + 1, 7, 1)  # 18 months in

    if now >= mid_date:
        start  = cycle_start
        reason = "past midpoint of current triannual cycle"
    else:
        start  = cycle_start - 3
        reason = "before midpoint — using previous triannual cycle"

    end = start + 2
    print(f"[review] Target tri-year: {start}–{end}  ({reason})")
    return start, end


# ---------------------------------------------------------------------------
# Path builders  (all use Saturday as week anchor, matching sort.py)
# ---------------------------------------------------------------------------

def week_review_path(sat):
    year  = sat.year
    month = sat.month
    q     = (month - 1) // 3 + 1
    mname = sat.strftime('%B')
    wnum  = week_number(sat)
    directory = os.path.join(OUTPUT_DIR, str(year), f"Q{q}", f"{month:02d}_{mname}")
    filename  = f"week_{wnum:02d}_summary.md"
    return os.path.join(directory, filename), wnum


def month_review_path(year, month):
    q         = (month - 1) // 3 + 1
    mname     = datetime(year, month, 1).strftime('%B')
    directory = os.path.join(OUTPUT_DIR, str(year), f"Q{q}", f"{month:02d}_{mname}")
    filename  = f"{month:02d}_{mname}_summary.md"
    return os.path.join(directory, filename), mname


def quarter_review_path(year, quarter):
    directory = os.path.join(OUTPUT_DIR, str(year), f"Q{quarter}")
    filename  = f"Q{quarter}_summary.md"
    return os.path.join(directory, filename)


def year_review_path(year):
    directory = os.path.join(OUTPUT_DIR, str(year))
    filename  = f"{year}_summary.md"
    return os.path.join(directory, filename)


def tri_year_review_path(start, end):
    # Placed under the start year's directory
    directory = os.path.join(OUTPUT_DIR, str(start))
    filename  = f"{start}-{end}_summary.md"
    return os.path.join(directory, filename)


# ---------------------------------------------------------------------------
# Template rendering
# ---------------------------------------------------------------------------

def render_template(template_name, replacements):
    path = os.path.join(TEMPLATE_DIR, template_name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Template not found: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, str(value))
    return content


def write_review_file(target_path, content, period_label):
    if os.path.exists(target_path):
        print(f"[review] WARNING: {target_path} already exists — skipping to avoid overwrite.")
        print(f"         Delete or rename it manually if you want a fresh copy.")
        return False
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[review] {period_label} review written → {target_path}")
    return True


# ---------------------------------------------------------------------------
# Per-period setup
# ---------------------------------------------------------------------------

def setup_week(now=None):
    sat     = target_week(now)
    sun     = week_sunday(sat)
    wnum    = week_number(sat)
    path, _ = week_review_path(sat)
    content = render_template('weekly.md', {'[[week_number]]': f"{wnum:02d}"})
    write_review_file(path, content, f"Week {wnum:02d} ({sun.strftime('%m-%d-%Y')}–{sat.strftime('%m-%d-%Y')})")


def setup_month(now=None):
    year, month   = target_month(now)
    path, mname   = month_review_path(year, month)
    content       = render_template('monthly.md', {'[[month_name]]': mname})
    write_review_file(path, content, f"{mname} {year}")


def setup_quarter(now=None):
    year, quarter = target_quarter(now)
    path          = quarter_review_path(year, quarter)
    content       = render_template('quarterly.md', {'[[quarter]]': f"Q{quarter}"})
    write_review_file(path, content, f"Q{quarter} {year}")


def setup_year(now=None):
    year    = target_year(now)
    path    = year_review_path(year)
    content = render_template('annually.md', {'[[year]]': str(year)})
    write_review_file(path, content, str(year))


def setup_tri(now=None):
    start, end = target_tri_year(now)
    path       = tri_year_review_path(start, end)
    content    = render_template('triannually.md', {'[[tri_year]]': f"{start}-{end}"})
    write_review_file(path, content, f"Tri-year {start}–{end}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

PERIODS = {
    'week':    setup_week,
    'month':   setup_month,
    'quarter': setup_quarter,
    'year':    setup_year,
    'tri':     setup_tri,
}

def setup_review(period, now=None):
    """Run sort first, then create the review file for the given period."""
    from sort import run_sort

    print("=" * 60)
    print(f"REVIEW: setting up {period} review")
    print("=" * 60)

    # Always sort pending entries before opening a review
    run_sort()

    print()
    if period not in PERIODS:
        raise ValueError(f"Invalid period {period!r}. Choose from: {', '.join(PERIODS)}")
    PERIODS[period](now)
    print("\n✅ Review setup complete.")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in PERIODS:
        print(f"Usage: python review.py [{' | '.join(PERIODS)}]")
        sys.exit(1)
    setup_review(sys.argv[1])
