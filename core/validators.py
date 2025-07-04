from django.core.validators import RegexValidator


hexadecimal_validator = RegexValidator(
    regex=r'^[0-9A-Fa-f]+$',
    message='Разрешены только шестнадцатеричные цифры.'
)

digits_validator = RegexValidator(
    regex=r'^\d+$',
    message='Разрешены только цифры.'
)
