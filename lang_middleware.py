from typing import Tuple, Any
from aiogram import types
from aiogram.contrib.middlewares.i18n import I18nMiddleware

import main

I18N_DOMAIN = 'valentinebot'
LOCALES_DIR = 'locales'


class ACLMiddleware(I18nMiddleware):
    async def get_user_locale(self, action: str, args: Tuple[Any]):
        if types.User.get_current().language_code in ['ru', 'uk']:
            return types.User.get_current().language_code
        else:
            return 'ru'

def setup_middleware(dp):
    i18n = ACLMiddleware(I18N_DOMAIN, LOCALES_DIR)
    dp.middleware.setup(i18n)
    return i18n
