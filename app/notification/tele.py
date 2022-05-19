""" Telegram Notification """
import asyncio
import time
import os
import pandas as pd
from app.config import LOG
from app.config import TG_CHANNEL_NAME
from telethon import TelegramClient


async def send_notif(signals):
    """ Function to send notification via telegram Bot

    Params:
        signals(list): List of signal generated with format ['pairName - $lasPrice - rsi - LONG/SHORT', etc...]
    Return:
        None  """
    LOG.info('Send notification via Telegram Bot')
    msg_header = """----- Signal RSI cross above 42.5 or below 57.5 -----

"""
    msg = """"""
    bot = TelegramClient('notify_bot', os.getenv(
        'TELE_API_ID'), os.getenv('TELE_API_HASH'))
    await bot.start(bot_token=os.getenv('TELE_BOT_TOKEN'))
    entity = await bot.get_entity(TG_CHANNEL_NAME)
    msg += msg_header
    for signal in signals:
        msg += "-> {} \n".format(signal)
    msg += f"""
>>> {str(pd.to_datetime(time.time(), unit='s').tz_localize('UTC').tz_convert('Asia/Jakarta').strftime('%m/%d/%Y %H:%M:%S'))}"""
    await bot.send_message(entity, msg)
    LOG.info('Success send notification via Telegram Bot')
