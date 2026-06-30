import pytest
import pandas as pd
import numpy as np
from atlas_quant.features.pipeline import FeaturePipeline
from atlas_quant.features.registry import registry

def test_pipeline_initialization():
    pipe = FeaturePipeline()
    assert len(pipe.get_feature_names()) == 0

def test_add_feature():
    pipe = FeaturePipeline()
    # Add a simple feature that doesn't require parameters
    # We'll use DailyReturn from price_structure
    pipe.add_feature('daily_return')
    assert len(pipe.get_feature_names()) == 1
    assert pipe.get_feature_names()[0] == 'daily_return'

def test_add_feature_with_params():
    pipe = FeaturePipeline()
    # Add SMA with period 20
    pipe.add_feature('sma', period=20, column='Close')
    assert len(pipe.get_feature_names()) == 1
    # The generated column name should be sma_20
    # We can check the feature instance's generated_columns
    feature = pipe._features[0]
    assert feature.generated_columns == ['sma_20']

def test_remove_feature():
    pipe = FeaturePipeline()
    pipe.add_feature('sma', period=20)
    pipe.add_feature('daily_return')
    assert len(pipe.get_feature_names()) == 2
    pipe.remove_feature('sma')
    assert len(pipe.get_feature_names()) == 1
    assert pipe.get_feature_names()[0] == 'daily_return'

def test_execute_pipeline():
    # Create a sample DataFrame
    df = pd.DataFrame({
        'Open': [1, 2, 3, 4, 5],
        'High': [2, 3, 4, 5, 6],
        'Low': [0.5, 1.5, 2.5, 3.5, 4.5],
        'Close': [1.5, 2.5, 3.5, 4.5, 5.5],
        'Volume': [100, 200, 300, 400, 500]
    })
    pipe = FeaturePipeline()
    pipe.add_feature('daily_return')
    pipe.add_feature('sma', period=3, column='Close')
    result = pipe.execute(df)
    # Check that the original columns are still there
    assert 'Open' in result.columns
    assert 'Close' in result.columns
    # Check that the new columns are added
    assert 'daily_return' in result.columns
    assert 'sma_3' in result.columns
    # Check that the values are not all NaN (except maybe first few)
    # Daily return: first row should be NaN
    assert pd.isna(result['daily_return'].iloc[0])
    # SMA: first two rows should be NaN (since period=3)
    assert pd.isna(result['sma_3'].iloc[0])
    assert pd.isna(result['sma_3'].iloc[1])
    # Third row should be the mean of first three closes: (1.5+2.5+3.5)/3 = 2.5
    assert abs(result['sma_3'].iloc[2] - 2.5) < 1e-9

def test_pipeline_returns_copy():
    df = pd.DataFrame({'Close': [1,2,3,4,5]})
    pipe = FeaturePipeline()
    pipe.add_feature('daily_return')
    result = pipe.execute(df)
    # Ensure original dataframe is not modified
    assert 'daily_return' not in df.columns
    assert 'daily_return' in result.columns
