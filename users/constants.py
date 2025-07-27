MAX_USER_USERNAME_LEN = 150
MIN_USER_USERNAME_LEN = 4
MAX_USER_EMAIL_LEN = 254
MAX_USER_PASSWORD_LEN = 128
MIN_USER_PASSWORD_LEN = 8
MAX_USER_ROLE_LEN = 16

MAX_USERS_PER_PAGE = 16

MAX_USER_USERNAME_DISPLAY_LEN = MAX_USER_USERNAME_LEN - 20
MIN_USER_AGE = 18
MAX_USER_AGE = 120

USERNAME_HELP_TEXT = (
    'Имя пользователя должно содержать минимум '
    f'{MIN_USER_USERNAME_LEN} символов. '
    'Допустимые символы: латинские буквы, цифры и .-_'
)
PASSWORD_HELP_TEXT = (
    f'Пароль должен содержать минимум {MIN_USER_PASSWORD_LEN} '
    'символов, не может быть полностью числовым, '
    'не должен быть похож на имя пользователя и '
    'не должен быть слишком простым.'
)

ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png']
