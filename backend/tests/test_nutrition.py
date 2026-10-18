"""
Tests for Nutrition Estimation Service.
Verifies IFCT lookup, serving size scaling, and mathematical proportionality on known test fixtures.
"""
import pytest
from backend.app.services.nutrition_service import NutritionService

@pytest.fixture
def nutrition_svc():
    return NutritionService()

def test_nutrition_lookup_regular(nutrition_svc):
    """Verifies standard regular serving lookup for Vada Pav."""
    nut = nutrition_svc.get_nutrition("Vada Pav", serving_size="Regular")
    assert nut["is_available"] is True
    assert nut["food_name"] == "Vada Pav"
    assert nut["serving_size"] == "Regular"
    assert nut["serving_weight_g"] == 135
    assert nut["calories"] == 305
    assert nut["protein"] == 6.3
    assert nut["carbohydrates"] == 45.8
    assert nut["fat"] == 11.2
    assert "IFCT 2017" in nut["data_source"]

def test_nutrition_serving_size_variations(nutrition_svc):
    """Verifies that Small, Regular, and Large servings return distinct, monotonically increasing portions."""
    small = nutrition_svc.get_nutrition("Pav Bhaji", serving_size="Small")
    regular = nutrition_svc.get_nutrition("Pav Bhaji", serving_size="Regular")
    large = nutrition_svc.get_nutrition("Pav Bhaji", serving_size="Large")

    assert small["serving_weight_g"] < regular["serving_weight_g"] < large["serving_weight_g"]
    assert small["calories"] < regular["calories"] < large["calories"]
    assert small["protein"] < regular["protein"] < large["protein"]

def test_mathematical_nutrition_scaling_fixture(nutrition_svc):
    """
    CRITICAL TEST: Mathematically verifies nutrition scaling using a known test fixture.
    Baseline: Idli Regular = 130g, 170 kcal, 5.8g protein, 35.5g carbs, 0.8g fat.
    Target custom weight: 260g (exactly 2.0x).
    Expected values: 340 kcal, 11.6g protein, 71.0g carbs, 1.6g fat.
    """
    scaled = nutrition_svc.scale_nutrition_by_weight("Idli", target_weight_g=260.0)

    assert scaled["is_available"] is True
    assert scaled["scaling_ratio"] == 2.0
    assert scaled["serving_weight_g"] == 260.0
    assert scaled["calories"] == pytest.approx(340.0, rel=1e-2)
    assert scaled["protein"] == pytest.approx(11.6, rel=1e-2)
    assert scaled["carbohydrates"] == pytest.approx(71.0, rel=1e-2)
    assert scaled["fat"] == pytest.approx(1.6, rel=1e-2)

def test_unknown_food_nutrition_withheld(nutrition_svc):
    """Verifies that unknown or unclassified foods return structured withheld nutritional values."""
    nut = nutrition_svc.get_nutrition("Other / Unknown Food", serving_size="Regular")
    assert nut["is_available"] is False
    assert nut["calories"] is None
    assert nut["protein"] is None
    assert "withheld" in nut["notes_uncertainty"].lower()
