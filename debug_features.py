#!/usr/bin/env python3
"""
Debug script to check feature calculation and signal generation
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

# Add the project root to sys.path so that atlas_quant can be imported
project_root = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(project_root))

from atlas_quant.data.manager import MarketDataManager
from atlas_quant.features.pipeline import FeaturePipeline
from atlas_quant.decision.engine import DecisionEngine
from atlas_quant.strategies.example_strategy import ExampleStrategy

def main():
    print("Debugging feature calculation and signal generation")
    print("=" * 50)

    # Define parameters
    start_date = "2016-01-01"
    end_date = "2016-12-31"
    symbols = ["AAPL", "MSFT", "GOOGL"]  # Skip AMZN for now due to download issues

    # Load data
    data_manager = MarketDataManager()
    market_data = {}
    for symbol in symbols:
        try:
            data = data_manager.get_data(
                ticker=symbol,
                start=start_date,
                end=end_date
            )
            market_data[symbol] = data
            print(f"Loaded {symbol}: {data.shape}")
        except Exception as e:
            print(f"Failed to load {symbol}: {e}")
            continue

    if not market_data:
        print("No data loaded!")
        return

    # Get features for one date to see what's available
    sample_date = list(market_data.values())[0].index[50]  # Pick a date in the middle
    print(f"\nSample date: {sample_date}")

    # Prepare historical data up to sample_date
    historical_data = {}
    for symbol, data in market_data.items():
        hist_data = data.loc[:sample_date]
        if len(hist_data) > 0:
            historical_data[symbol] = hist_data

    print(f"Historical data for {len(historical_data)} symbols")

    # Calculate features using the pipeline
    try:
        # Create a feature pipeline and add the required features
        from atlas_quant.features.pipeline import FeaturePipeline
        from atlas_quant.features.registry import registry
        pipeline = FeaturePipeline()

        # Add the required features: rsi, sma_50, sma_200
        # These should be available in the feature registry
        try:
            pipeline.add_feature('rsi')
            pipeline.add_feature('sma', period=50)
            pipeline.add_feature('sma', period=200)
            print("Added features: rsi, sma_50, sma_200")
        except Exception as e:
            print(f"Could not add features via pipeline: {e}")
            print("Available features:", list(registry._registry.keys()))
            # Fall back to manual calculation of basic features
            featured_data = {}
            for symbol, data in historical_data.items():
                # Calculate basic features manually for debugging
                import pandas as pd
                import numpy as np
                df = data.copy()
                # Calculate SMA 50 and 200
                df['sma_50'] = df['Close'].rolling(window=50).mean()
                df['sma_200'] = df['Close'].rolling(window=min(200, len(df))).mean()
                # Calculate RSI 14
                delta = df['Close'].diff()
                gain = delta.where(delta > 0, 0)
                loss = -delta.where(delta < 0, 0)
                avg_gain = gain.rolling(window=14).mean()
                avg_loss = loss.rolling(window=14).mean()
                rs = avg_gain / avg_loss.replace(0, np.nan)
                df['rsi_14'] = 100 - (100 / (1 + rs))
                featured_data[symbol] = df

        # Calculate features for each symbol
        featured_data = {}
        for symbol, data in historical_data.items():
            # Apply feature pipeline
            try:
                featured = pipeline.execute(data)
                featured_data[symbol] = featured
                print(f"{symbol} features shape: {featured.shape}")
                print(f"{symbol} feature columns: {list(featured.columns)}")
                print(f"{symbol} sample feature values (last row):")
                for col in featured.columns[-5:]:  # Show last 5 columns
                    print(f"  {col}: {featured[col].iloc[-1]:.2f}")
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                # Fall back to manual calculation of basic features
                import pandas as pd
                import numpy as np
                df = data.copy()
                # Calculate SMA 50 and 200 (adjust window if insufficient data)
                df['sma_50'] = df['Close'].rolling(window=min(50, len(df))).mean()
                df['sma_200'] = df['Close'].rolling(window=min(200, len(df))).mean()
                # Calculate RSI 14
                delta = df['Close'].diff()
                gain = delta.where(delta > 0, 0)
                loss = -delta.where(delta < 0, 0)
                avg_gain = gain.rolling(window=min(14, len(df))).mean()
                avg_loss = loss.rolling(window=min(14, len(df))).mean()
                rs = avg_gain / avg_loss.replace(0, np.nan)
                df['rsi_14'] = 100 - (100 / (1 + rs))
                featured_data[symbol] = df
    except Exception as e:
        print(f"Error calculating features: {e}")
        import traceback
        traceback.print_exc()
        return

    # Now test the decision engine
    try:
        strategy = ExampleStrategy()
        decision_engine = DecisionEngine(strategy=strategy)

        # Process the featured data
        result = decision_engine.process(featured_data)
        print(f"\nDecision engine result keys: {result.keys()}")
        if 'scores' in result:
            print(f"Scores: {result['scores']}")
        if 'target_weights' in result:
            print(f"Target weights: {result['target_weights']}")
    except Exception as e:
        print(f"Error in decision engine: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()