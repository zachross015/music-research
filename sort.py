import os
import csv
import re
import shutil
from datetime import datetime, timedelta
from collections import defaultdict

INPUT_DIR = '.'
SCRATCHPAD = 'scratchpad.md'
ARCHIVE_DIR = 'archive'
OUTPUT_DIR = 'journal'
DRAFTS_PREFIX = 'DraftsExport'

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def parse_scratchpad():
    if not os.path.exists(SCRATCHPAD):
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
    
    return parsed

def parse_drafts_exports():
    entries = []
    for fname in os.listdir(INPUT_DIR):
        if fname.startswith(DRAFTS_PREFIX) and fname.endswith('.csv'):
            full_path = os.path.join(INPUT_DIR, fname)
            file_entries = []

            with open(full_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    created_at = row.get('created_at')
                    content = row.get('content')
                    if not created_at or not content:
                        continue
                    try:
                        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        file_entries.append((dt, content.strip()))
                    except ValueError:
                        print(f"Skipping malformed datetime: {created_at}")

            if file_entries:
                entries.extend(file_entries)
                os.remove(full_path)
                print(f"Processed and deleted: {fname}")
            else:
                print(f"No valid entries in {fname}, not deleted.")
    return entries


def load_week_file(path):
    if not os.path.exists(path):
        return {}
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entries = re.split(r'\n(?=# \d{2}-\d{2}-\d{4})', content.strip())
    date_to_body = {}

    for entry in entries:
        lines = entry.strip().split('\n')
        if not lines:
            continue
        header = lines[0].strip()
        match = re.match(r'# (\d{2})-(\d{2})-(\d{4})', header)
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

def organize_entries(entries):
    entries_by_start_date = defaultdict(list)
    for dt, body in entries:
        iso = dt.isocalendar()
        year = iso[0]
        week = iso[1]
        start_date = datetime.fromisocalendar(year, week, 1)
        date_str = dt.strftime('%m-%d-%Y')
        header = f"# {date_str}"
        entries_by_start_date[start_date].append((dt, header, body))
    return entries_by_start_date

def process_entries(entries):
    entries_by_start_date = organize_entries(entries)

    for start_date, day_entries in entries_by_start_date.items():
        quarter = (start_date.month - 1) // 3 + 1
        month_str = f"{start_date.month:02d}_{start_date.strftime('%B')}"
        year_dir = os.path.join(OUTPUT_DIR, str(start_date.year), f"Q{quarter}", month_str)
        ensure_dir(year_dir)
        week_num = start_date.isocalendar()[1]
        week_file = os.path.join(year_dir, f"week_{week_num:02d}.md")

        existing = load_week_file(week_file)

        # Sort entries chronologically by creation time
        sorted_entries = sorted(day_entries, key=lambda x: x[0])
        
        for dt, header, body in sorted_entries:
            if header in existing:
                existing[header] += f"\n\n{body}"
            else:
                existing[header] = body

        write_week_file(week_file, existing)

def archive_scratchpad():
    if not os.path.exists(SCRATCHPAD):
        return
    ensure_dir(ARCHIVE_DIR)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    archived = os.path.join(ARCHIVE_DIR, f"scratchpad_{timestamp}.md")
    shutil.move(SCRATCHPAD, archived)
    open(SCRATCHPAD, 'w', encoding='utf-8').close()
    print(f"Archived scratchpad to {archived}")

def main():
    scratch_entries = parse_scratchpad()
    draft_entries = parse_drafts_exports()
    all_entries = scratch_entries + draft_entries

    if not all_entries:
        print("No journal entries found.")
        return

    process_entries(all_entries)
    if scratch_entries:
        archive_scratchpad()

    print("✅ Journal import complete.")

if __name__ == '__main__':
    main()
