import re
from django.contrib import messages
from django.contrib.messages import constants


def password_is_valid(request, password, confirm_password):
    if len(password) < 6:
        messages.add_message(request, constants.ERROR,
                             'Sua senha deve conter, no mínimo 8  caractertes, e deve conter pelo menos 1 letra maiúscula, 1 minúscula e números')
        return False

    if not password == confirm_password:
        messages.add_message(request, constants.ERROR,
                             'As senhas não coincidem!')
        return False

    if not re.search('[A-Z]', password):
        messages.add_message(request, constants.ERROR,
                             'Sua senha não contém letras maiúsculas')
        return False

    if not re.search('[a-z]', password):
        messages.add_message(request, constants.ERROR,
                             'Sua senha não contem letras minúsculas')
        return False

    if not re.search('[1-9]', password):
        messages.add_message(request, constants.ERROR,
                             'Sua senha não contém números')
        return False

    return True
