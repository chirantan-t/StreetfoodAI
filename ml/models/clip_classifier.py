"""
CLIP Zero-Shot Classifier for Indian Street Food.
Uses OpenAI CLIP via Hugging Face Transformers.
Features:
- Indian street food domain-specific prompt engineering
- Text embedding caching and L2 normalization
- Zero-shot cosine similarity classification
- Architectural documentation on zero-shot limitations and explainability differences
"""
from typing import List, Dict, Tuple, Optional
import torch
import torch.nn.functional as F
from PIL import Image

# Prompt templates tailored for Indian Street Food recognition
STREET_FOOD_PROMPT_TEMPLATES = [
    "a photo of {food}, a traditional Indian street food dish",
    "a delicious plate of Indian street food {food}",
    "a street food vendor serving fresh {food} in India",
    "an authentic Indian snack called {food}",
    "a close up photograph of {food} served with chutney"
]

class StreetFoodCLIPClassifier:
    """
    Zero-shot classifier leveraging contrastive language-image pretraining (CLIP).
    """
    def __init__(
        self,
        model_name: str = "openai/clip-vit-base-patch32",
        classes: Optional[List[str]] = None,
        device: Optional[str] = None
    ):
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.classes = classes or []
        self.model = None
        self.processor = None
        self.text_features = None

    def load(self):
        """Loads CLIP model and tokenizer/processor."""
        from transformers import CLIPModel, CLIPProcessor
        print(f"Loading CLIP model {self.model_name} onto {self.device}...")
        self.model = CLIPModel.from_pretrained(self.model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(self.model_name)
        self.model.eval()

        if self.classes:
            self._compute_text_features()

    def set_classes(self, classes: List[str]):
        """Sets target food categories and precomputes text embeddings."""
        self.classes = classes
        if self.model is not None:
            self._compute_text_features()

    def _compute_text_features(self):
        """
        Generates ensemble text embeddings by averaging across multiple
        domain-adapted prompt templates for each food class.
        """
        all_class_features = []
        with torch.no_grad():
            for food_name in self.classes:
                # Handle unknown class specifically
                if "unknown" in food_name.lower():
                    prompts = [
                        "a photo of an unfamiliar non-food object",
                        "a random object or background that is not Indian street food",
                        "an unidentifiable miscellaneous item"
                    ]
                else:
                    prompts = [template.format(food=food_name) for template in STREET_FOOD_PROMPT_TEMPLATES]

                inputs = self.processor(text=prompts, return_tensors="pt", padding=True).to(self.device)
                prompt_embeddings = self.model.get_text_features(**inputs)
                # Normalize each prompt embedding
                prompt_embeddings = prompt_embeddings / prompt_embeddings.norm(dim=-1, keepdim=True)
                # Average prompt embeddings for this class
                mean_embedding = prompt_embeddings.mean(dim=0, keepdim=True)
                mean_embedding = mean_embedding / mean_embedding.norm(dim=-1, keepdim=True)
                all_class_features.append(mean_embedding)

            self.text_features = torch.cat(all_class_features, dim=0) # [num_classes, embed_dim]

    def predict_image(self, image: Image.Image, top_k: int = 5) -> List[Dict]:
        """
        Runs zero-shot inference for a single PIL image.
        Returns top-k predictions with confidence scores.
        """
        if self.model is None or self.text_features is None:
            raise RuntimeError("CLIP model or text features not loaded. Call load() first.")

        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)

            # Cosine similarity scaled by logit_scale
            logit_scale = self.model.logit_scale.exp()
            logits = logit_scale * (image_features @ self.text_features.T)
            probabilities = F.softmax(logits, dim=-1).squeeze(0)

        top_probs, top_indices = torch.topk(probabilities, k=min(top_k, len(self.classes)))

        results = []
        for prob, idx in zip(top_probs.tolist(), top_indices.tolist()):
            results.append({
                "class_name": self.classes[idx],
                "confidence": round(float(prob), 4),
                "class_index": int(idx)
            })

        return results
