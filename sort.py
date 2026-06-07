import os
import csv
import re
import shutil
from datetime import datetime, timedelta, timezone
from collections import defaultdict

INPUT_DIR = '.'
SCRATCHPAD = 'scratchpad.md'
ARCHIVE_DIR = 'archive'
OUTPUT_DIR = 'journal'
DRAFTS_PREFIX = 'DraftsExport'


# ---------------------------------------------------------------------------
# Week math
# ---------------------------------------------------------------------------

def week_saturday(dt):
    """Return the Saturday that closes the Sun–Sat week containing dt."""
    # weekday(): Mon=0 … Sun=6
    # Days until Saturday from any given day:
    #   Mon→5, Tue→4, Wed→3, Thu→2, Fri→1, Sat→0, Sun→6
    days_ahead = (5 - dt.weekday()) % 7
    return (dt + timedelta(days=days_ahead)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

def week_sunday(saturday):
    """Return the Sunday that opens the week whose Saturday is given."""
    return saturday - timedelta(days=6)

def week_number(saturday):
    """
    Week number for the week whose closing Saturday is the given date.
    Week 1 is the week whose Saturday first falls in the new year
    (i.e. the first Saturday >= Jan 1).  Weeks are 0-padded to 2 digits.
    """
    year = saturday.year
    jan1 = datetime(year, 1, 1)
    # First Saturday of this year
    first_sat = jan1 + timedelta(days=(5 - jan1.weekday()) % 7)
    delta = (saturday - first_sat).days
    return delta // 7 + 1   # 1-based


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def normalize(dt):
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def to_naive(dt):
    """Convert any datetime to a naive local-time datetime for consistent week math."""
    if dt.tzinfo is not None:
        dt = dt.astimezone().replace(tzinfo=None)
    return dt

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"  [dir] Created directory: {path}")

def week_file_path(saturday):
    """
    Build the full path for a week file based on its closing Saturday.
    Directory structure: journal/YYYY/Q#/MM_MonthName/week_NN.md
    """
    year   = saturday.year
    month  = saturday.month
    q      = (month - 1) // 3 + 1
    mname  = saturday.strftime('%B')
    wnum   = week_number(saturday)
    return os.path.join(
        OUTPUT_DIR,
        str(year),
        f"Q{q}",
        f"{month:02d}_{mname}",
        f"week_{wnum:02d}.md"
    )


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_scratchpad():
    if not os.path.exists(SCRATCHPAD):
        print("[scratchpad] scratchpad.md not found, skipping.")
        return []

    with open(SCRATCHPAD, 'r', encoding='utf-8') as f:
        content = f.read()

    entries = re.split(r'\n(?=# \d{2}-\d{2}-\d{4})', content.strip())
    parsed = []

    for entry in entries:
        lines = entry.strip().split('\n')
        if not lines:
            continue
        header = lines[0].strip()
        match = re.match(r'# (\d{2})-(\d{2})-(\d{4})', header)
        if not match:
            continue
        month, day, year = match.groups()
        dt = datetime.strptime(f"{year}-{month}-{day}", '%Y-%m-%d')
        body = '\n'.join(lines[1:]).strip()
        parsed.append((dt, body))
        print(f"  [scratchpad] Parsed entry dated {dt.strftime('%m-%d-%Y')}")

    print(f"[scratchpad] {len(parsed)} entr{'y' if len(parsed)==1 else 'ies'} parsed.")
    return parsed


def parse_drafts_exports():
    """Parse all DraftsExport CSVs. Returns (entries, source_files) where
    source_files is the list of CSV paths to delete after a successful write."""
    entries      = []
    source_files = []
    csv_files = [
        f for f in os.listdir(INPUT_DIR)
        if f.startswith(DRAFTS_PREFIX) and f.endswith('.csv')
    ]

    if not csv_files:
        print("[drafts] No DraftsExport CSV files found.")
        return entries, source_files

    for fname in csv_files:
        full_path = os.path.join(INPUT_DIR, fname)
        file_entries = []
        print(f"[drafts] Processing {fname} …")

        with open(full_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                created_at = row.get('created_at')
                content    = row.get('content')
                if not created_at or not content:
                    continue
                try:
                    dt = to_naive(datetime.fromisoformat(created_at.replace("Z", "+00:00")))
                    file_entries.append((dt, content.strip()))
                    print(f"  [drafts] Parsed entry dated {dt.strftime('%m-%d-%Y %H:%M')}")
                except ValueError:
                    print(f"  [drafts] WARNING: Skipping malformed datetime: {created_at!r}")

        if file_entries:
            entries.extend(file_entries)
            source_files.append(full_path)
            print(f"  [drafts] {len(file_entries)} entr{'y' if len(file_entries)==1 else 'ies'} queued from {fname}; will delete after successful write.")
        else:
            print(f"  [drafts] No valid entries in {fname}; file kept.")

    return entries, source_files


# ---------------------------------------------------------------------------
# Week file I/O
# ---------------------------------------------------------------------------

def load_week_file(path):
    if not os.path.exists(path):
        return {}

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    entries     = re.split(r'\n(?=# \d{2}-\d{2}-\d{4})', content.strip())
    date_to_body = {}

    for entry in entries:
        lines  = entry.strip().split('\n')
        if not lines:
            continue
        header = lines[0].strip()
        match  = re.match(r'# (\d{2})-(\d{2})-(\d{4})', header)
        if not match:
            continue
        body = '\n'.join(lines[1:]).strip()
        date_to_body[header] = body

    return date_to_body


def write_week_file(path, merged_entries):
    sorted_entries = sorted(
        merged_entries.items(),
        key=lambda x: datetime.strptime(x[0][2:], '%m-%d-%Y')
    )
    with open(path, 'w', encoding='utf-8') as f:
        for header, body in sorted_entries:
            f.write(f"{header}\n\n{body.strip()}\n\n")


# ---------------------------------------------------------------------------
# Organise & write
# ---------------------------------------------------------------------------

def organize_entries(entries):
    """Group entries by the Saturday that closes their Sun–Sat week."""
    by_saturday = defaultdict(list)
    for dt, body in entries:
        sat        = week_saturday(dt)
        date_str   = dt.strftime('%m-%d-%Y')
        header     = f"# {date_str}"
        by_saturday[sat].append((dt, header, body))
    return by_saturday


def process_entries(entries):
    by_saturday = organize_entries(entries)

    for sat, day_entries in sorted(by_saturday.items()):
        path    = week_file_path(sat)
        sun     = week_sunday(sat)
        wnum    = week_number(sat)
        print(f"\n[sort] Week {wnum:02d}  ({sun.strftime('%m-%d-%Y')} – {sat.strftime('%m-%d-%Y')})  →  {path}")

        ensure_dir(os.path.dirname(path))
        existing = load_week_file(path)
        prev_count = len(existing)

        sorted_entries = sorted(day_entries, key=lambda x: normalize(x[0]))

        new_days     = 0
        appended_days = 0
        for dt, header, body in sorted_entries:
            if header in existing:
                existing[header] += f"\n\n{body}"
                print(f"  [sort]   Appended content to existing day {header[2:]}")
                appended_days += 1
            else:
                existing[header] = body
                print(f"  [sort]   Added new day entry {header[2:]}")
                new_days += 1

        write_week_file(path, existing)
        print(f"  [sort]   Week file written: {new_days} new day(s), {appended_days} appended, {prev_count} pre-existing.")


# ---------------------------------------------------------------------------
# Scratchpad archiving
# ---------------------------------------------------------------------------

def archive_scratchpad():
    if not os.path.exists(SCRATCHPAD):
        return
    ensure_dir(ARCHIVE_DIR)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    archived  = os.path.join(ARCHIVE_DIR, f"scratchpad_{timestamp}.md")
    shutil.move(SCRATCHPAD, archived)
    open(SCRATCHPAD, 'w', encoding='utf-8').close()
    print(f"[scratchpad] Archived to {archived} and reset.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run_sort():
    """Parse all pending sources and sort entries into week files."""
    print("=" * 60)
    print("SORT: importing journal entries")
    print("=" * 60)

    scratch_entries            = parse_scratchpad()
    draft_entries, draft_files = parse_drafts_exports()
    all_entries                = scratch_entries + draft_entries

    if not all_entries:
        print("\n[sort] No journal entries found. Nothing to do.")
        return

    print(f"\n[sort] Total entries to process: {len(all_entries)}")
    process_entries(all_entries)

    # Only clean up source files after all writes have succeeded
    for fpath in draft_files:
        os.remove(fpath)
        print(f"[drafts] Deleted source file: {os.path.basename(fpath)}")

    if scratch_entries:
        archive_scratchpad()

    print("\n✅ Sort complete.")


def main():
    run_sort()

if __name__ == '__main__':
    main()
