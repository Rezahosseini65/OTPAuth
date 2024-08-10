from django.core.validators import RegexValidator


class PhoneNumberValidator(RegexValidator):
    regex = r"^\+989\d{9}$"
    message = "Phone number must be entered in the format: '+989xxxxxxxxx'. Up to 12 digits allowed."
    code = "phone_number_is_invalid"


phone_number_validator = PhoneNumberValidator()