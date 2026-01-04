import os
import shutil
from datetime import datetime

# Number of days at the start of a period to consider as buffer for previous period. Must be between 0 and 6.
BUFFER_DAYS = 4

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'journal_by_week', 'templates')

def get_month_name_for(year, month):
    """Get the month name string for a given year and month."""
    return f"{month:02d}_{datetime(year, month, 1).strftime('%B')}"

def get_week_number():
    """Get the current week number of the year, adjusting for first 4 days."""
    now = datetime.now()
    iso = now.isocalendar()
    year = now.year
    if iso[2] <= BUFFER_DAYS:
        print("Buffer period triggered: using previous week.")
        # Previous week
        if iso[1] == 1:
            year -= 1
            last_week = datetime(year, 12, 31).isocalendar()[1]
            return last_week, year
        else:
            return iso[1] - 1, year
    else:
        return iso[1], year

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
    val, year = config['get_func']()
    journal_dir = os.path.join(BASE_DIR, 'journal_by_week', str(year))
    
    if period == 'week':
        week_date = datetime.fromisocalendar(year, val, 1)
        month = week_date.month
        month_str = get_month_name_for(year, month)
        target_file = os.path.join(journal_dir, month_str, f"week_{val}_summary.md")
        replacement = str(val)
    elif period == 'month':
        month_num = int(val.split('_')[0])
        month_only = datetime(year, month_num, 1).strftime('%B')
        target_file = os.path.join(journal_dir, f"{val}_summary.md")
        replacement = month_only
    elif period == 'quarter':
        target_file = os.path.join(journal_dir, f"Q{val}_summary.md")
        replacement = f"Q{val}"
    elif period == 'year':
        target_file = os.path.join(journal_dir, f"{val}_summary.md")
        replacement = str(val)
    elif period == 'tri':
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