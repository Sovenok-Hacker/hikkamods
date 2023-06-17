from .. import loader
import logging, asyncio, re

from telethon.tl.functions.channels import JoinChannelRequest
from telethon.errors.rpcerrorlist import UsernameNotOccupiedError
from enum import Enum

logger = logging.getLogger(__name__)


class Patterns(Enum):
    DELETED_ACTIVATED = re.compile(r'Вы не можете активировать этот чек снова|Чек уже активирован|Чек удалён')
    NOT_SUBSCRIBED = re.compile(r'Вы не состоите в требуемых группах для активации этого чека')
    NEED_PASSWORD = re.compile(r'Данный чек защищён паролем, введите его!')
    CHEQUE = re.compile(r'xЧек')
    WAIT = re.compile(r'Loading')
    SUCCESS = re.compile(r'/^Вы получили\s+(\d+(\.\d+)?)\s+([\S ]*?)\s*(\w+)?$/gm')
def parse(msg):
    for p in Patterns:
        if re.findall(p.value, msg):
            return p

def parse_value(m):
    mat = re.match(Patterns.SUCCESS.value, m)
    if mat:
        value = int(mat.group(1)) if mat.group(1).isnumeric() else float(mat.group(1))
        ticker = mat.group(4) or None
        return value, ticker

async def activate(code, client, ll, password=None):
    async with client.conversation('@xJetSwapBot') as c:
        await c.send_message(f'/start {code}')
        m = await c.get_response()
        stat = parse(m.message)

        if stat == Patterns.DELETED_ACTIVATED:
            if "❌" in ll:
                logger.error('Чек удалён или уже активирован')
            return

        if stat == Patterns.NOT_SUBSCRIBED:
            for b in m.buttons:
                if b[0].url:
                    try:
                        await client(JoinChannelRequest(b[0].url))
                        if "🪲" in ll:
                            logger.info(f'Подписались на {b[0].url}')
                    except ValueError:
                        if "❌" in ll:
                            logger.error(f'Канал или группа {b[0].url} не существует')
                        return
                else:
                    await b[0].click()
            m = await c.get_response()
            stat = parse(m.message)

        if stat == Patterns.NEED_PASSWORD:
            if password:
                await c.send_message(password)
                if "🪲" in ll:
                    logger.info('Ввели пароль')
                m = await c.get_response()
                stat = parse(m.message)
            else:
                if "⚠️" in ll:
                    logger.warning('Необходим пароль, но он отсутствует')
                return

        if stat == Patterns.WAIT:
            while stat == Patterns.WAIT:
                if "🪲" in ll:
                    logger.info('Ожидаем чек ...')
                m = await c.get_response()
                stat = parse(m.message)
                await asyncio.sleep(0.2)

        if stat == Patterns.CHEQUE:
            await m.buttons[0][0].click()
            if "🪲" in ll:
                logger.info('Нажали на кнопку активации ...')
            m = await c.get_response()
            stat = parse(m.message)

        if stat == Patterns.SUCCESS:
            if "✅" in ll:
                logger.info(f'Чек успешно активирован, получено {" ".join(parse_value(m.message))}')
            await m.delete()

@loader.tds
class sh_actxJetSwapModule(loader.Module):
    """Активатор чеков @xJetSwapBot"""
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "Logging",
                [],
                "Ведение журнала",
                validator=loader.validators.MultiChoice(["❌", "⚠️", "✅", "🪲"]),
            ),
        )
    strings = {
        "name": "sh_actxJetSwap",
    }
    async def client_ready(self, client, db):
        self.client = client
        await client.send_message('xJetSwapBot', '/start')

    async def watcher(self, message):
        if not message.__class__.__name__ == "Message":
            return
        if message.raw_text and 'https://t.me/xJetSwapBot?start=' in message.raw_text:
            if match := re.search(r'https://t\.me/xJetSwapBot\?start=(c_[A-Za-z0-9_/]+)', message.message):
                await activate(match.group(1), self.client, self.config["Logging"])
        elif message.buttons and message.buttons[0][0].url:
            if match := re.search(r'https://t\.me/xJetSwapBot\?start=(c_[A-Za-z0-9_/]+)', message.buttons[0][0].url):
                await activate(match.group(1), self.client, self.config["Logging"])

    async def checkactxJetcmd(self, message):
        """Проверить работоспособность"""
        await message.edit("<b>🦉Совиный активатор чеков @xJetSwapBot работает!\nРежим логирования: {''.join(self.config['Logging'])}</b>")
