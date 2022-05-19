""" testing for strategy.alert """

from app.connector import ExchangeConnector
from app.strategy.indicator_alert import IndicatorAlert
import pytest
import ccxt
import asyncio

ohlcvs = ExchangeConnector(
    'binance', market_type='future').data('1h', '/BUSD')


def test_calculate_indicator():
    """ Test calculate indicator """
    result = asyncio.get_event_loop().run_until_complete(
        IndicatorAlert()._calculate_indicator(ohlcvs[0]))
    assert len(result) != 0


def test_signal():
    """ test signal """
    calculate = IndicatorAlert()._calculate_indicator(ohlcvs[0])
    result = asyncio.get_event_loop().run_until_complete(calculate)
    assert IndicatorAlert()._signal([calculate]) != None


def test_seri():
    """ Test series create for handling signal """
    assert len(IndicatorAlert()._seri(40.5, ohlcvs[0])) != 0


def test_main():
    """ Test _main function """
    result = asyncio.get_event_loop().run_until_complete(
        IndicatorAlert()._main(ohlcvs))
    assert result != None


def test_calculate():
    """  """
    assert IndicatorAlert.calculate(ohlcvs) != None
