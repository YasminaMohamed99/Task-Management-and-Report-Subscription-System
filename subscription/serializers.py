import re
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    start_date = serializers.CharField()
    report_time = serializers.CharField()

    class Meta:
        model = Subscription
        fields = ['start_date', 'frequency', 'report_time']

    def to_internal_value(self, data):
        """
            Perform validation on start_date, frequency, and report_time fields.
            - Validates the start_date format to be 'YYYY-MM-DD HH:00:00'.
            - Ensures frequency is one of the valid choices: 'daily', 'weekly', or 'monthly'.
            - Validates and extracts the report_time hour (0-23) from different formats.
        """
        start_date = data.get('start_date')
        frequency = data.get('frequency')
        report_time = data.get('report_time')
        errors = []
        if start_date:
            # Regex pattern to validate 'YYYY-MM-DD HH:00:00' format with valid month, day, and hour
            date_regex = r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01]) (00|01|02|03|04|05|06|07|08|09|1[0-9]|2[0-3]):00:00$'
            if not re.match(date_regex, start_date):
                errors.append("start_date must be in the format 'YYYY-MM-DD HH:00:00', with minutes and seconds as 00.")
        else:
            errors.append("start_date is a required field.")

        if frequency:
            # Validate frequency: must be one of the valid choices
            valid_frequencies = ['daily', 'weekly', 'monthly']
            if frequency not in valid_frequencies:
                errors.append(f"frequency must be one of {valid_frequencies}.")
        else:
            errors.append("frequency is a required field.")

        if report_time:
            # If report_time is given as an integer, convert it to a string
            if isinstance(report_time, int):
                report_time = str(report_time)

            # Validate report time to supports 12-hour (AM/PM) and 24-hour formats.
            if not re.match("^((0?[1-9]|1[0-2])\s?(AM|PM)|([01]?[0-9]|2[0-3])(:00(:00)?)?)$", report_time):
                errors.append("Invalid report time format. Expected one of the following: 'H AM/PM', 'H:00:00', 'H:00', 'H', where H is an hour between 0 and 23.")
            else:
                # Extract hour from report time to save as int in db
                hour = extract_hour(report_time)
        else:
            errors.append("report_time is a required field.")

        # Raise validation error if any issues are found
        if errors:
            raise serializers.ValidationError({"errors": errors})

        # Assign the validated report_time hour as an integer to the data
        data['report_time'] = hour

        return data


def extract_hour(report_time):
    """
        Extracts the hour from the report_time string. Supports 12-hour (AM/PM) and 24-hour formats.
        - Converts 'AM/PM' time into 24-hour format.
        - Handles cases with or without space between hour and AM/PM.
        - Returns an integer representing the hour in 24-hour format.
    """
    if 'AM' in report_time or 'PM' in report_time:
        # Extract the hour before AM/PM
        am_pm = 'AM' if 'AM' in report_time else 'PM'
        hour = int(report_time.replace(am_pm, '').strip())
        if am_pm == 'PM' and hour != 12:
            hour += 12  # Convert PM hour to 24-hour format (except 12 PM)
        if am_pm == 'AM' and hour == 12:
            hour = 0  # 12 AM is 0 in 24-hour format
    else:
        if ":" in report_time:
            hour = int(report_time.split(':')[0])
        else:
            hour = int(report_time)

    return hour
