"""
Nutrition Estimation Service for StreetFoodAI.
References the Indian Food Composition Tables (IFCT 2017, ICMR-NIN) and documented composite datasets.
Provides portion scaling across Small, Regular, and Large servings.
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

class NutritionService:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Default location
            db_path = str(Path(__file__).resolve().parent.parent.parent.parent / "ml" / "config" / "nutrition_db.json")

        self.db_path = Path(db_path)
        self.disclaimer = ""
        self.foods: Dict[str, Any] = {}
        self.id_to_food: Dict[str, str] = {}
        self._load_database()

    def _load_database(self):
        if not self.db_path.exists():
            print(f"Warning: Nutrition database not found at {self.db_path}")
            return

        with open(self.db_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.disclaimer = data.get("disclaimer", "")
        self.foods = data.get("foods", {})

        for name, info in self.foods.items():
            self.id_to_food[info["id"]] = name
            self.id_to_food[name.lower()] = name

    def get_food_names(self) -> List[str]:
        return list(self.foods.keys())

    def get_all_foods(self) -> Dict[str, Any]:
        return {
            "disclaimer": self.disclaimer,
            "foods": self.foods
        }

    def get_nutrition(
        self,
        food_name_or_id: str,
        serving_size: str = "Regular"
    ) -> Dict[str, Any]:
        """
        Retrieves nutritional estimation for a given food and serving size.
        Serving sizes supported: 'Small', 'Regular', 'Large'.
        """
        serving_size = serving_size.capitalize()
        if serving_size not in ["Small", "Regular", "Large"]:
            serving_size = "Regular"

        # Resolve food name
        resolved_name = self.foods.get(food_name_or_id)
        if not resolved_name:
            canonical_name = self.id_to_food.get(food_name_or_id.lower())
            if canonical_name and canonical_name in self.foods:
                food_info = self.foods[canonical_name]
                food_name = canonical_name
            else:
                food_info = self.foods.get("Other / Unknown Food")
                food_name = "Other / Unknown Food"
        else:
            food_info = resolved_name
            food_name = food_name_or_id

        # Unknown / Unclassified handling
        if food_name == "Other / Unknown Food" or food_info is None:
            return {
                "food_id": "other_unknown",
                "food_name": "Other / Unknown Food",
                "category": "Unclassified",
                "serving_size": serving_size,
                "serving_description": "Unrecognized or uncertain food item",
                "serving_weight_g": None,
                "calories": None,
                "protein": None,
                "carbohydrates": None,
                "fat": None,
                "fiber": None,
                "data_source": "N/A",
                "source_reference": "N/A",
                "notes_uncertainty": "Nutritional calculation is withheld for uncertain items to prevent inaccurate dietary logging.",
                "disclaimer": self.disclaimer,
                "is_available": False
            }

        servings = food_info.get("servings", {})
        portion = servings.get(serving_size)

        # Fallback to regular if portion missing
        if not portion and "Regular" in servings:
            portion = servings["Regular"]
            serving_size = "Regular"

        return {
            "food_id": food_info.get("id"),
            "food_name": food_name,
            "category": food_info.get("category", "Street Food"),
            "serving_size": serving_size,
            "serving_description": food_info.get("serving_description", ""),
            "serving_weight_g": portion.get("serving_weight_g") if portion else None,
            "calories": portion.get("calories") if portion else None,
            "protein": portion.get("protein") if portion else None,
            "carbohydrates": portion.get("carbohydrates") if portion else None,
            "fat": portion.get("fat") if portion else None,
            "fiber": portion.get("fiber") if portion else None,
            "data_source": food_info.get("data_source", "IFCT 2017 (ICMR-NIN)"),
            "source_reference": food_info.get("source_reference", ""),
            "notes_uncertainty": food_info.get("notes_uncertainty", ""),
            "disclaimer": self.disclaimer,
            "is_available": True
        }

    def scale_nutrition_by_weight(
        self,
        food_name: str,
        target_weight_g: float
    ) -> Dict[str, Any]:
        """
        Scales macronutrients proportionally based on explicit mass in grams.
        Calculates ratio relative to regular serving size.
        """
        regular_nut = self.get_nutrition(food_name, serving_size="Regular")
        if not regular_nut["is_available"] or not regular_nut["serving_weight_g"]:
            return regular_nut

        base_weight = regular_nut["serving_weight_g"]
        ratio = target_weight_g / base_weight

        return {
            **regular_nut,
            "serving_size": f"Custom ({target_weight_g:.0f}g)",
            "serving_weight_g": round(target_weight_g, 1),
            "calories": round(regular_nut["calories"] * ratio, 1) if regular_nut["calories"] else None,
            "protein": round(regular_nut["protein"] * ratio, 1) if regular_nut["protein"] else None,
            "carbohydrates": round(regular_nut["carbohydrates"] * ratio, 1) if regular_nut["carbohydrates"] else None,
            "fat": round(regular_nut["fat"] * ratio, 1) if regular_nut["fat"] else None,
            "fiber": round(regular_nut["fiber"] * ratio, 1) if regular_nut["fiber"] else None,
            "scaled_proportionally": True,
            "scaling_ratio": round(ratio, 3)
        }
