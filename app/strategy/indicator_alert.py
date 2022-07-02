""" Create alert """
import asyncio
import logging
import pandas as pd
import pandas_ta as ta
from app.config import *
from app.connector import ExchangeConnector


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
            ohlcv['rsi'] = ta.rsi(ohlcv.close, RSI).round(
                decimals=2)  # calculate RSI
            ohlcv['ema_fast'] = ta.ema(ohlcv.close, EMA_FAST).round(decimals=int(
                (len(str(ohlcv.close[-1:].values[0]).split('.')[1]))))  # calculate EMA & round result same as price
            ohlcv['ema_slow'] = ta.ema(ohlcv.close, EMA_SLOW).round(decimals=int(
                (len(str(ohlcv.close[-1:].values[0]).split('.')[1]))))  # calculate EMA & round result same as price
            ohlcv['ema_trend'] = ohlcv.apply(
                lambda x: 'up' if x['ema_fast'] > x['ema_slow'] else 'down', axis=1)  # up if ema fast above ema slow
            ohlcv['timestamp'] = pd.to_datetime(ohlcv['timestamp'], unit='ms').dt.tz_localize(
                'UTC').dt.tz_convert('Asia/Jakarta')
            ohlcv['rsi_up'] = ta.cross(
                ohlcv.rsi, self._seri(42.5, ohlcv), asint=False)
            ohlcv['rsi_down'] = ta.cross(self._seri(
                57.5, ohlcv), ohlcv.rsi, asint=False)
            return ohlcv[-2:-1]
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
            result = []
            for ohlcv in ohlcvs:
                if len(ohlcv) >= EMA_SLOW:
                    last = ohlcv[-2:-1]
                    # check LONG or SHORT signal
                    if (last.rsi_up.values[0] and last.ema_trend.values[0] == 'up'):
                        result.append(
                            f'{ohlcv.name} - ${ohlcv.close[-1:].values[0]} - {ohlcv.rsi[-1:].values[0]} - LONG')
                    elif (last.rsi_down.values[0] and last.ema_trend.values[0] == 'down'):
                        result.append(
                            f'{ohlcv.name} - ${ohlcv.close[-1:].values[0]} - {ohlcv.rsi[-1:].values[0]} - SHORT')
            return result
        except Exception as e:
            LOG.exception(e)

    async def _main(self, ohlcvs):
        """  """

        new_ohlcvs = [await self._calculate_indicator(ohlcv) for ohlcv in ohlcvs if len(ohlcv) > EMA_SLOW]
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
