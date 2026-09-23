from datetime import datetime
def format_date(date):
    if not date:
        return "N/A"

    try:
        date_obj = datetime.fromisoformat(
            date.replace("Z", "+00:00")
        )
    except ValueError:
        date_obj = datetime.strptime(
            date,
            "%d/%m/%Y %H:%M:%S"
        )

    return date_obj.strftime("%d/%m/%Y %H:%M:%S")

def parse_date_safe(date_str):
    if not date_str or date_str == "N/A":
        return None
    if isinstance(date_str, datetime):
        return date_str
    try:
        return datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S")
    except (ValueError, TypeError):
        pass
    try:
        return datetime.fromisoformat(str(date_str).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None