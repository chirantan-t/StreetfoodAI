"""
Integration Tests for FastAPI Endpoints.
Verifies health checks, food listing, prediction, explainability, and history endpoints.
"""
import io
from PIL import Image
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database.session import init_db

# Ensure test database tables are created
init_db()

client = TestClient(app)

def test_api_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "StreetFoodAI"
    assert data["num_classes"] == 20
    assert len(data["supported_classes"]) == 20

def test_api_supported_foods_endpoint():
    response = client.get("/api/foods")
    assert response.status_code == 200
    data = response.json()
    assert "disclaimer" in data
    assert "foods" in data
    assert "Vada Pav" in data["foods"]

def test_api_nutrition_lookup_endpoint():
    response = client.get("/api/nutrition/Samosa?serving_size=Regular")
    assert response.status_code == 200
    data = response.json()
    assert data["food_name"] == "Samosa"
    assert data["calories"] == 290
    assert data["serving_size"] == "Regular"

def test_api_predict_endpoint():
    # Synthetic test image
    buf = io.BytesIO()
    img = Image.new("RGB", (150, 150), color="orange")
    img.save(buf, format="JPEG")
    buf.seek(0)

    files = {"image": ("test_dish.jpg", buf, "image/jpeg")}
    data = {"serving_size": "Regular"}
    response = client.post("/api/predict", files=files, data=data)

    assert response.status_code == 200
    resp_json = response.json()
    assert "predicted_food" in resp_json
    assert "confidence" in resp_json
    assert "nutrition" in resp_json
    assert "top_candidates" in resp_json

def test_api_history_lifecycle():
    # 1. Create a record
    record_payload = {
        "food_name": "Vada Pav",
        "confidence": 0.92,
        "serving_size": "Regular",
        "serving_weight_g": 135.0,
        "calories": 305.0,
        "protein": 6.3,
        "carbohydrates": 45.8,
        "fat": 11.2,
        "fiber": 3.2,
        "is_uncertain": False,
        "model_architecture": "mobilenet_v3_large",
        "notes": "Unit test record"
    }

    create_res = client.post("/api/history", json=record_payload)
    assert create_res.status_code == 201
    created_item = create_res.json()
    record_id = created_item["id"]
    assert created_item["food_name"] == "Vada Pav"

    # 2. Get history list and find created item
    get_res = client.get("/api/history")
    assert get_res.status_code == 200
    history_list = get_res.json()
    assert any(r["id"] == record_id for r in history_list)

    # 3. Delete record
    del_res = client.delete(f"/api/history/{record_id}")
    assert del_res.status_code == 200

    # 4. Verify deletion
    del_verify_res = client.delete(f"/api/history/{record_id}")
    assert del_verify_res.status_code == 404
