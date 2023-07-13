# meta developer: @yummy_gay и @Duo_sova

import re
from .. import loader
import logging

from tgchequeman import exceptions, activate_multicheque, parse_url

logger = logging.getLogger(__name__)

async def activate(code, client, ll):
    if not (code.startswith("mci") or code.startswith("t")):
        if "⚠️" in ll:
            logger.warning(f"{code}: Не чек и не мульти-чек, пропускаем ...")
        return
    bot_url = parse_url("https://t.me/tonRocketBot?start=" + code)
    try:
        await activate_multicheque(
            client=client,
            bot_url=bot_url,
            password=None
        )
    except (exceptions.ChequeFullyActivatedOrNotFound, exceptions.PasswordError) as err:
        if "❌" in ll:
            logger.error(f"Ошибка: {err}")
        return
    except (exceptions.ChequeActivated,
            exceptions.ChequeForPremiumUsersOnly,
            exceptions.CannotActivateOwnCheque) as warn:
        if "⚠️" in ll:
            logger.warning(f"Предупреждение: {warn}")
        return
    except exceptions.UnknownError as err:
        if "❌" in ll:
            logger.error(f"Ошибка: {err}")
        return
    except Exception as err:
        if "❌" in ll:
            logger.error(f"Ошибка: {err}")
        return
    if "✅" in ll:
        logger.info("Чек успешно активирован!")

@loader.tds
class sh_actTonRocketModule(loader.Module):
    """Активатор чеков @tonRocketBot с автоматической подпиской (и если вы не премиум пользователь автоматически решается капча)"""
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "ll",
                [],
                "Ведение журнала",
                validator=loader.validators.MultiChoice(["❌", "⚠️", "✅"]),
            ),
        )
    strings = {
        "name": "sh_actTonRocket",
    }
    async def client_ready(self, client, db):
        self.client = client
        await client.send_message('tonRocketBot', '/start')

    async def watcher(self, message):
        if not message.__class__.__name__ == "Message":
            return
        if message.raw_text and 'https://t.me/tonRocketBot?start=' in message.raw_text:
            if match := re.search(r'https://t.me/tonRocketBot\?start=([A-Za-z0-9_/]+)', message.raw_text):
                await activate(match.group(1), self.client, self.config["ll"])
        elif message.buttons and message.buttons[0][0].url:
            if match := re.search(r'https://t.me/tonRocketBot\?start=([A-Za-z0-9_/]+)', message.buttons[0][0].url):
                await activate(match.group(1), self.client, self.config["ll"])

    async def checkactTonRocketcmd(self, message):
        """проверить работоспособность"""
        await message.edit("<b>Активатор чеков @tonRocketBot работает! 🦉</b>")
