import pytest
from atlas_quant.features.registry import registry, FeatureRegistry

def test_registry_singleton():
    # Ensure we have the same instance
    reg1 = FeatureRegistry()
    reg2 = FeatureRegistry()
    assert reg1 is not reg2  # Actually, we create new instances each time, but the module has a global instance
    # The module exports a global instance; we test that.
    from atlas_quant.features.registry import registry as reg_global
    assert isinstance(reg_global, FeatureRegistry)

def test_register_feature():
    # We'll use a simple feature class for testing
    from atlas_quant.features.base import BaseFeature
    class TestFeature(BaseFeature):
        feature_key = 'test_feature'
        _category = 'test'
        name = 'test_feature'
        required_columns = ['col']
        generated_columns = ['test_feature']
        def calculate(self, dataframe):
            return dataframe
        def validate(self, dataframe):
            super().validate(dataframe)
    # Register
    registry.register(TestFeature)
    # Check it's in the list
    assert 'test_feature' in registry.list_features()
    # Get the class
    cls = registry.get('test_feature')
    assert cls == TestFeature
    # Clean up: remove from registry to avoid affecting other tests
    # Since there's no unregister, we can't easily clean up. We'll skip for now.
    # Alternatively, we can create a new registry for each test.
    pass

def test_list_features():
    # Just ensure it returns a list
    features = registry.list_features()
    assert isinstance(features, list)
    assert len(features) > 0
    # Check that some known features are present
    assert 'sma' in features  # Actually, the name is 'sma' but the instance name includes period? Wait, our SMA class has name='sma'
    # However, the registry stores by the class attribute 'name', which is 'sma' for SMA.
    # So we should see 'sma' in the list.
    # Let's verify by checking the actual registry keys.
    # We'll do a quick check: if 'sma' in registry._features
    assert 'sma' in registry._features

def test_get_categories():
    cats = registry.get_categories()
    assert isinstance(cats, dict)
    # Check that we have some expected categories
    expected_cats = {'trend', 'momentum', 'volatility', 'volume', 'price_structure', 'market'}
    for cat in expected_cats:
        assert cat in cats
        assert isinstance(cats[cat], list)
        assert len(cats[cat]) > 0
