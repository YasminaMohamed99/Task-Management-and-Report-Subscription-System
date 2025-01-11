import re
from datetime import datetime
from django.db.models import Q
from rest_framework.exceptions import ParseError


def parse_date(date_str):
    """
       Parses the input date string in the format YYYY-MM-DD.
       Raises a ParseError if the date string is not in the correct format or if the date is invalid (e.g., incorrect month or day).
    """
    if not re.match(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])", date_str):
        raise ParseError("Invalid date format. Please use YYYY-MM-DD format, and ensure that the month is between 01 and 12 and the day is between 01 and 31.")
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ParseError("Invalid date format. Please use YYYY-MM-DD format, and ensure that the month is between 01 and 12 and the day is between 01 and 31.")


def filter_by_date_range(queryset, start_date, end_date):
    """Filters the given queryset by a date range based on the provided start and end dates."""
    try:
        if start_date:
            start_date = parse_date(start_date)
        if end_date:
            end_date = parse_date(end_date)

        if start_date and end_date:
            queryset = queryset.filter(
                Q(start_date__gte=start_date) & (Q(completion_date__lte=end_date) | Q(due_date__lte=end_date)))
        elif start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        elif end_date:
            queryset = queryset.filter(Q(completion_date__lte=end_date) | Q(due_date__lte=end_date))

        return queryset

    except ParseError as parse_error:
        raise ParseError(str(parse_error))
    except Exception as e:
        raise Exception(str(e))
