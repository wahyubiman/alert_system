""" Create alert """
import asyncio
import logging
import pandas as pd
import pandas_ta as ta
from app.config import *
from app.connector import ExchangeConnector
from scipy.signal import argrelmax, argrelmin


class IndicatorAlert:

    async def _calculate_indicator(self, ohlcv):
        """ Function for calculating indicator value from dataframe

        Params:
            ohlcv(Pandas.DataFrame): list of pandas dataframe OHLCV
        Returns:
            ohlcv(pandas.DataFrame): return dataframe that contain OHLCV & indicator value """

        if PROD == False:
            LOG.info(
                f"Calculate indicator for {ohlcv.name}")
        try:
            """ ohlcv['rsi'] = ta.rsi(ohlcv.close, RSI).round(
                decimals=2)  # calculate RSI """
            ohlcv['ema_fast'] = ta.ema(ohlcv.close, EMA_FAST).round(decimals=int(
                (len(str(ohlcv.close[-1:].values[0]).split('.')[1]))))  # calculate EMA & round result same as price
            """ ohlcv['ema_slow'] = ta.ema(ohlcv.close, EMA_SLOW).round(decimals=int(
                (len(str(ohlcv.close[-1:].values[0]).split('.')[1]))))  # calculate EMA & round result same as price
            ohlcv['ema_trend'] = ohlcv.apply(
                lambda x: 'up' if x['ema_fast'] > x['ema_slow'] else 'down', axis=1)  # up if ema fast above ema slow """
            ohlcv['timestamp'] = pd.to_datetime(ohlcv['timestamp'], unit='ms').dt.tz_localize(
                'UTC').dt.tz_convert('Asia/Jakarta')
            """ ohlcv['rsi_up'] = ta.cross(
                ohlcv.rsi, self._seri(42.5, ohlcv), asint=False)
            ohlcv['rsi_down'] = ta.cross(self._seri(
                57.5, ohlcv), ohlcv.rsi, asint=False) """
            ohlcv['ph'] = ohlcv.iloc[argrelmax(
                ohlcv.high.values, order=5)].high
            ohlcv['pl'] = ohlcv.iloc[argrelmin(
                ohlcv.low.values, order=5)].low
            ohlcv['ph'] = ohlcv['ph'].fillna(method='ffill')
            ohlcv['pl'] = ohlcv['pl'].fillna(method='ffill')
            ohlcv['break_h'] = ta.cross(ohlcv.close, ohlcv.ph)
            ohlcv['break_l'] = ta.cross(ohlcv.pl, ohlcv.close)
            return ohlcv
        except Exception as e:
            LOG.exception(e)
            pass

    def _seri(self, value, ohlcv):
        return pd.Series(value, index=ohlcv.index,
                         name=f"{value}".replace(".", "_"))

    async def _signal(self, ohlcvs):
        """ Function for calculate signal

        Params:
            ohlc(List): list of pandas dataframe contain result from indicator
        Returns:
            result(list): list pair name with format ['pairName - $lasPrice - rsi - LONG/SHORT']"""

        LOG.info('Calculating signal . . .')
        try:
            result_up = []
            result_down = []
            for ohlcv in ohlcvs:
                last = ohlcv[-3:-2]
                # check LONG or SHORT signal
                if (last.break_h.values[0] == 1) & (last.ema_fast.values[0] < last.close.values[0]):
                    result_up.append(
                        f'{ohlcv.name} - ${last.close.values[0]} on {last.timestamp[-1:].dt.strftime("%d/%m/%Y %H:%M:%S").astype(str).values[0]}')
                elif (last.break_l.values[0] == 1) & (last.ema_fast.values[0] > last.close.values[0]):
                    result_down.append(
                        f'{ohlcv.name} - ${last.close.values[0]} on {last.timestamp[-1:].dt.strftime("%d/%m/%Y %H:%M:%S").astype(str).values[0]}')
            return [result_up, result_down]
        except Exception as e:
            LOG.exception(e)

    async def _main(self, ohlcvs):
        """  """

        new_ohlcvs = [await self._calculate_indicator(ohlcv) for ohlcv in ohlcvs if len(ohlcv) > EMA_FAST]
        signal = await self._signal(ohlcvs)
        return signal

    @classmethod
    def calculate(cls, ohlcvs):
        """  Function for calculating indicator and define signal at specified condition

        Params:
            ohlcvs(List): list of Pandas.DataFrame

        Returns:
            result(List): list of pair name """

        result = asyncio.run(
            cls()._main(ohlcvs))
        return result
