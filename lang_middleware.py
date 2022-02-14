from pathlib import Path
from typing import Tuple, Any
from aiogram import types
from aiogram.contrib.middlewares.i18n import I18nMiddleware

import postgres

I18N_DOMAIN = 'valentinesbot'

BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / 'locales'

class ACLMiddleware(I18nMiddleware):
    async def get_user_locale(self, action: str, args: Tuple[Any]):

        user = types.User.get_current()
        db_locale = await postgres.get_user_language(user.id)


        if user.language_code in ['ru', 'uk']:
            tg_locale =  user.language_code
        else:
            tg_locale =  'uk'
        print(tg_locale)
        return db_locale or tg_locale

def setup_middleware(dp):
    i18n = ACLMiddleware(I18N_DOMAIN, LOCALES_DIR)
    dp.middleware.setup(i18n)
    return i18n
