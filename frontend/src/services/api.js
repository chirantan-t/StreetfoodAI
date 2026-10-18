/**
 * API Client for StreetFoodAI backend communication.
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

export async function fetchHealth() {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}

export async function fetchSupportedFoods() {
  const res = await fetch(`${API_BASE_URL}/foods`);
  if (!res.ok) throw new Error(`Failed to fetch foods: ${res.statusText}`);
  return res.json();
}

export async function fetchFoodNutrition(foodName, servingSize = 'Regular') {
  const res = await fetch(`${API_BASE_URL}/nutrition/${encodeURIComponent(foodName)}?serving_size=${servingSize}`);
  if (!res.ok) throw new Error(`Failed to fetch nutrition: ${res.statusText}`);
  return res.json();
}

export async function predictImage(file, servingSize = 'Regular') {
  const formData = new FormData();
  formData.append('image', file);
  formData.append('serving_size', servingSize);

  const res = await fetch(`${API_BASE_URL}/predict`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Prediction error (${res.status}): ${res.statusText}`);
  }
  return res.json();
}

export async function explainImage(file, targetClassIndex = null) {
  const formData = new FormData();
  formData.append('image', file);
  if (targetClassIndex !== null && targetClassIndex !== undefined) {
    formData.append('target_class_index', targetClassIndex.toString());
  }

  const res = await fetch(`${API_BASE_URL}/explain`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Explainability error (${res.status}): ${res.statusText}`);
  }
  return res.json();
}

export async function fetchHistory() {
  const res = await fetch(`${API_BASE_URL}/history`);
  if (!res.ok) throw new Error(`Failed to fetch history: ${res.statusText}`);
  return res.json();
}

export async function saveHistory(record) {
  const res = await fetch(`${API_BASE_URL}/history`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(record),
  });
  if (!res.ok) throw new Error(`Failed to save history: ${res.statusText}`);
  return res.json();
}

export async function deleteHistory(id) {
  const res = await fetch(`${API_BASE_URL}/history/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(`Failed to delete record: ${res.statusText}`);
  return res.json();
}

export async function fetchAnalytics() {
  const res = await fetch(`${API_BASE_URL}/analytics`);
  if (!res.ok) throw new Error(`Failed to fetch analytics: ${res.statusText}`);
  return res.json();
}
