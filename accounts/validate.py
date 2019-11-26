import re
from string import punctuation
from django.core.exceptions import ValidationError


def validate_bio(value):
    if len(value) < 10:
        raise ValidationError("Add more detail to your bio.")


def validate_date(value):
    pattern = r'(\d{2}/d{2}/d{4})|(\d{4}-\d{2}-\d{2})|(\d{2}/d{2}/d{2})'

    result = re.match(pattern, str(value))
    if not result:
        msg = "Invalid date format: MM/DD/YY; MM/DD/YYYY; YYYY-MM-DD"
        raise ValidationError(msg)


class ValidatePasswordCharacters:

    def validate(self, password, user=None):
        password_error_msg = 'Your password must include:'
        regex1 = (r'\d+', ' at least one digit [0-9]')
        regex2 = (r'[A-Z]+', ' at least one uppercase letter [A-Z]')
        regex3 = (r'[a-z]+', ' at least one lowercase letter [a-z]')
        regex4 = (r'\W+', ' at least one special character [{punctuation}]')

        for pattern in (regex1, regex2, regex3, regex4):
            regex = re.compile(pattern[0])
            result = re.search(regex, password)
            if not result:
                raise ValidationError(f'{password_error_msg}{pattern[1]}')
            continue
        return None

    def get_help_text(self):
        return """A password must at least one digit, one uppercase letter,
        one lowercase letter, and one special character"""
