"""Feature package initialization.

Registers all feature classes with the global registry.
"""

from .registry import registry

# Import feature modules to trigger registration via class definitions
# However, we need to explicitly register because the classes don't self-register.
# We'll import each module and register the known classes.

from .trend import (
    SMA, EMA, WMA, MACD,
    MovingAverageDistance, MovingAverageSlope,
    PriceAboveMA, GoldenCross, DeathCross
)

from .momentum import (
    RSI, ROC, Momentum, StochasticOscillator
)

from .volatility import (
    ATR, HistoricalVolatility, BollingerBands
)

from .volume import (
    VolumeSMA, RelativeVolume, OnBalanceVolume,
    MoneyFlowIndex, ChaikinMoneyFlow
)

from .price_structure import (
    DailyReturn, LogReturn, IntradayReturn, Gap,
    CandleBody, UpperWick, LowerWick, RangePercent,
    DistanceTo52WeekHigh, DistanceTo52WeekLow
)

from .market import (
    RelativeStrength, Beta, RollingCorrelation,
    ExcessReturn, TrackingError
)

# Register all imported classes
registry.register(SMA)
registry.register(EMA)
registry.register(WMA)
registry.register(MACD)
registry.register(MovingAverageDistance)
registry.register(MovingAverageSlope)
registry.register(PriceAboveMA)
registry.register(GoldenCross)
registry.register(DeathCross)

registry.register(RSI)
registry.register(ROC)
registry.register(Momentum)
registry.register(StochasticOscillator)

registry.register(ATR)
registry.register(HistoricalVolatility)
registry.register(BollingerBands)

registry.register(VolumeSMA)
registry.register(RelativeVolume)
registry.register(OnBalanceVolume)
registry.register(MoneyFlowIndex)
registry.register(ChaikinMoneyFlow)

registry.register(DailyReturn)
registry.register(LogReturn)
registry.register(IntradayReturn)
registry.register(Gap)
registry.register(CandleBody)
registry.register(UpperWick)
registry.register(LowerWick)
registry.register(RangePercent)
registry.register(DistanceTo52WeekHigh)
registry.register(DistanceTo52WeekLow)

registry.register(RelativeStrength)
registry.register(Beta)
registry.register(RollingCorrelation)
registry.register(ExcessReturn)
registry.register(TrackingError)
