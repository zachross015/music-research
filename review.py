import os
import shutil
from datetime import datetime

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'journal_by_week', 'templates')
JOURNAL_DIR = os.path.join(BASE_DIR, 'journal_by_week', '2025')

def get_week_number():
    """Get the current week number of the year."""
    return datetime.now().isocalendar()[1]

def get_month_name():
    """Get the current month name."""
    return datetime.now().strftime('%m_%B')

def get_quarter():
    """Get the current quarter."""
    month = datetime.now().month
    return (month - 1) // 3 + 1

def setup_review(period):
    """Set up the review for the given period."""
    if period == 'week':
        template_file = os.path.join(TEMPLATE_DIR, 'weekly.md')
        week_number = get_week_number()
        target_dir = os.path.join(JOURNAL_DIR, get_month_name())
        target_file = os.path.join(target_dir, f"week_{week_number}_summary.md")
        placeholder = '[[week_number]]'
        replacement = str(week_number)
    elif period == 'month':
        template_file = os.path.join(TEMPLATE_DIR, 'monthly.md')
        month_name = get_month_name()
        target_file = os.path.join(JOURNAL_DIR, f"{month_name}_summary.md")
        placeholder = '[[month_name]]'
        replacement = month_name
    elif period == 'quarter':
        template_file = os.path.join(TEMPLATE_DIR, 'quarterly.md')
        quarter = get_quarter()
        target_file = os.path.join(JOURNAL_DIR, f"Q{quarter}_summary.md")
        placeholder = '[[quarter]]'
        replacement = f"Q{quarter}"
    elif period == 'year':
        template_file = os.path.join(TEMPLATE_DIR, 'annually.md')
        year = datetime.now().year
        target_file = os.path.join(JOURNAL_DIR, f"{year}_summary.md")
        placeholder = '[[year]]'
        replacement = str(year)
    elif period == 'tri':
        template_file = os.path.join(TEMPLATE_DIR, 'triannually.md')
        year = datetime.now().year
        tri_year = year - (year % 3)
        target_file = os.path.join(JOURNAL_DIR, f"{tri_year}-{tri_year + 2}_summary.md")
        placeholder = '[[tri_year]]'
        replacement = f"{tri_year}-{tri_year + 2}"
    else:
        raise ValueError("Invalid period. Choose from 'week', 'month', 'quarter', 'year', 'tri'.")

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