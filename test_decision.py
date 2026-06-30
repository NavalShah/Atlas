import pandas as pd
import numpy as np
from atlas_quant.strategies.example_strategy import ExampleStrategy
from atlas_quant.decision.engine import DecisionEngine

# Create a fake feature matrix for two assets
# Index: ticker
# Columns: features
data = {
    'AAPL': {
        'rsi_14': 60.0,
        'sma_50': 150.0,
        'sma_200': 140.0,
        'Close': 155.0,
        'Volume': 1_000_000.0,
        'volatility_14': 0.02
    },
    'MSFT': {
        'rsi_14': 40.0,
        'sma_50': 250.0,
        'sma_200': 260.0,
        'Close': 255.0,
        'Volume': 800_000.0,
        'volatility_14': 0.03
    }
}
# Convert to DataFrame where rows are assets, columns are features
df = pd.DataFrame.from_dict(data, orient='index')
print("Feature matrix:")
print(df)

# Create strategy
strategy = ExampleStrategy()
# Create engine
engine = DecisionEngine(strategy=strategy)

# Run the engine
result = engine.process(df)
print("\nScores:")
print(result['scores'])
print("\nRanked:")
print(result['ranked'])
print("\nTarget weights:")
print(result['target_weights'])
print("\nSized weights:")
print(result['sized_weights'])
