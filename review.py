import os
import shutil
from datetime import datetime, timedelta

# Number of days at the start of a period to consider as buffer for previous period. Must be between 0 and 6.
BUFFER_DAYS = 4

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'journal', 'templates')

def get_month_name_for(year, month):
    """Get the month name string for a given year and month."""
    return f"{month:02d}_{datetime(year, month, 1).strftime('%B')}"

def get_week_number():
    """Get the current week number of the year, adjusting for first 4 days."""
    now = datetime.now()
    year = now.year
    DD = timedelta(days=BUFFER_DAYS)
    date = now - DD
    iso = date.isocalendar()
    
    # Offset week number by -1 since we start counting at the first full week in the new year
    return (iso[1] - 1) % 52, year

def get_month_name():
    """Get the current month name, adjusting for first 4 days."""
    now = datetime.now()
    year = now.year
    if now.day <= BUFFER_DAYS:
        print("Buffer period triggered: using previous month.")
        # Previous month
        if now.month == 1:
            year -= 1
            prev_month = 12
            month_str = f"{prev_month:02d}_{datetime(year, prev_month, 1).strftime('%B')}"
            return month_str, year
        else:
            prev_month = now.month - 1
            month_str = f"{prev_month:02d}_{datetime(now.year, prev_month, 1).strftime('%B')}"
            return month_str, year
    else:
        month_str = now.strftime('%m_%B')
        return month_str, year

def get_quarter():
    """Get the current quarter, adjusting for first 4 days of quarter."""
    now = datetime.now()
    year = now.year
    month = now.month
    quarter = (month - 1) // 3 + 1
    quarter_start_month = (quarter - 1) * 3 + 1
    if month == quarter_start_month and now.day <= BUFFER_DAYS:
        print("Buffer period triggered: using previous quarter.")
        # Previous quarter
        if quarter == 1:
            quarter = 4
            year -= 1
        else:
            quarter -= 1
    return quarter, year

def get_year():
    """Get the current year, adjusting for first 4 days."""
    now = datetime.now()
    if now.month == 1 and now.day <= BUFFER_DAYS:
        print("Buffer period triggered: using previous year.")
        year = now.year - 1
        return year, year
    else:
        year = now.year
        return year, year

def get_tri_year():
    """Get the triannual year, adjusting for first 4 days."""
    now = datetime.now()
    year = now.year
    tri_year = year - (year % 3)
    folder_year = tri_year
    if year % 3 == 0 and now.month == 1 and now.day <= BUFFER_DAYS:
        print("Buffer period triggered: using previous triannual period.")
        tri_year -= 3
        folder_year = tri_year
    return tri_year, folder_year

def setup_review(period):
    """Set up the review for the given period."""
    period_config = {
        'week': {'template': 'weekly.md', 'placeholder': '[[week_number]]', 'get_func': get_week_number},
        'month': {'template': 'monthly.md', 'placeholder': '[[month_name]]', 'get_func': get_month_name},
        'quarter': {'template': 'quarterly.md', 'placeholder': '[[quarter]]', 'get_func': get_quarter},
        'year': {'template': 'annually.md', 'placeholder': '[[year]]', 'get_func': get_year},
        'tri': {'template': 'triannually.md', 'placeholder': '[[tri_year]]', 'get_func': get_tri_year},
    }
    
    if period not in period_config:
        raise ValueError("Invalid period. Choose from 'week', 'month', 'quarter', 'year', 'tri'.")
    
    config = period_config[period]
    template_file = os.path.join(TEMPLATE_DIR, config['template'])
    
    now = datetime.now()
    
    if period == 'tri':
        val, folder_year = config['get_func']()
        start_date = datetime(folder_year, 1, 1)
    else:
        val, year = config['get_func']()
        if period == 'week':
            start_date = now - timedelta(days=now.weekday())
        elif period == 'month':
            month_num = int(val.split('_')[0])
            start_date = datetime(year, month_num, 1)
        elif period == 'quarter':
            start_month = (val - 1) * 3 + 1
            start_date = datetime(year, start_month, 1)
        elif period == 'year':
            start_date = datetime(val, 1, 1)
    
    if period == 'week':
        quarter = (start_date.month - 1) // 3 + 1
        month_str = f"{start_date.month:02d}_{start_date.strftime('%B')}"
        journal_dir = os.path.join(BASE_DIR, 'journal', str(start_date.year), f"Q{quarter}", month_str)
        target_file = os.path.join(journal_dir, f"week_{val}_summary.md")
        replacement = str(val)
    elif period == 'month':
        quarter = (start_date.month - 1) // 3 + 1
        journal_dir = os.path.join(BASE_DIR, 'journal', str(start_date.year), f"Q{quarter}", val)
        target_file = os.path.join(journal_dir, f"{val}_summary.md")
        month_only = datetime(year, month_num, 1).strftime('%B')
        replacement = month_only
    elif period == 'quarter':
        journal_dir = os.path.join(BASE_DIR, 'journal', str(start_date.year), f"Q{val}")
        target_file = os.path.join(journal_dir, f"Q{val}_summary.md")
        replacement = f"Q{val}"
    elif period == 'year':
        journal_dir = os.path.join(BASE_DIR, 'journal', str(val))
        target_file = os.path.join(journal_dir, f"{val}_summary.md")
        replacement = str(val)
    elif period == 'tri':
        journal_dir = os.path.join(BASE_DIR, 'journal', str(folder_year))
        target_file = os.path.join(journal_dir, f"{val}-{val + 2}_summary.md")
        replacement = f"{val}-{val + 2}"
    
    placeholder = config['placeholder']

    # Ensure the target directory exists
    os.makedirs(os.path.dirname(target_file), exist_ok=True)

    # Read the template and replace placeholders
    with open(template_file, 'r') as template:
        content = template.read().replace(placeholder, replacement)

    # Write the new file
    with open(target_file, 'w') as new_file:
        new_file.write(content)

    print(f"{period.capitalize()} review created: {target_file}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python review.py [week|month|quarter|year|tri]")
    else:
        setup_review(sys.argv[1])