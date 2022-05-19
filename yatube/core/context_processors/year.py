from datetime import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    what_datetime_today = datetime.today()
    return {
        'year': what_datetime_today.year
    }