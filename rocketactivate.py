# meta developers: @yummy_gay and @Duo_sova

import re
from .. import loader
import logging

from tgchequeman import exceptions, activate_multicheque, parse_url

logger = logging.getLogger(__name__)

async def activate(code):
    bot_url = parse_url("https://t.me/tonRocketBot?start=" + code)
    try:
        await activate_multicheque(
            client=self.client,
            bot_url=bot_url,
            password=None
        )
    except (exceptions.ChequeFullyActivatedOrNotFound, exceptions.PasswordError) as err:
        logger.error(f"Ошибка: {err}")
    except (exceptions.ChequeActivated,
            exceptions.ChequeForPremiumUsersOnly,
            exceptions.CannotActivateOwnCheque) as warn:
        logger.warning(f"Предупреждение: {warn}")
        return
    except exceptions.UnknownError as err:
        logger.error(f"Ошибка: {err}")
        return
    except Exception as err:
        logger.error(f"Ошибка: {err}")

@loader.tds
class yg_actTonRocketModule(loader.Module):
    """Активатор чеков @tonRocketBot с автоматической подпиской (и если вы не премиум пользователь автоматически решается капча)"""

    strings = {
        "name": "sh_actTonRocket",
    }

    async def client_ready(self, client, db):
        self.client = client
        await client.send_message('tonRocketBot', '/start')

    async def watcher(self, message):
        if message.raw_text and 'https://t.me/tonRocketBot?start=' in message.raw_text:
            if match := re.search(r'https://t.me/tonRocketBot\?start=([A-Za-z0-9_/]+)', message.raw_text):
                await activate(match.group(1))
        elif message.buttons and message.buttons[0].url:
            if match := re.search(r'https://t.me/tonRocketBot\?start=([A-Za-z0-9_/]+)', message.buttons[0].url):
                await activate(match.group(1))

    async def checkactTonRocketcmd(self, message):
        """проверить работоспособность"""
        await message.edit("<b>Активатор чеков @tonRocketBot работает! 🦉</b>")
