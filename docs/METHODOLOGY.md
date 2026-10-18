# StreetFoodAI: Model Development & Training Methodology

## 1. Deep Learning Architectures

StreetFoodAI investigates three diverse paradigms:

### A. MobileNetV3-Large
* **Characteristics:** Depthwise separable convolutions, squeeze-and-excitation blocks, hard-swish activation.
* **Target Output:** 20 classes.
* **Head Replacement:**
  ```python
  model.classifier[2] = nn.Dropout(p=0.2)
  model.classifier[3] = nn.Linear(1280, num_classes)
  ```
* **Grad-CAM Layer:** Final convolutional block `model.features[-1]`.
* **Hardware Profile:** 4.23M parameters, 16.13 MB, 13.5ms CPU latency.

### B. EfficientNet-B0
* **Characteristics:** Compound scaling across network depth, channel width, and input image resolution using MBConv blocks.
* **Head Replacement:**
  ```python
  model.classifier[0] = nn.Dropout(p=0.2)
  model.classifier[1] = nn.Linear(1280, num_classes)
  ```
* **Grad-CAM Layer:** Final convolutional block `model.features[-1]`.
* **Hardware Profile:** 4.03M parameters, 15.39 MB, 21.1ms CPU latency.

### C. CLIP Zero-Shot (ViT-B/32)
* **Characteristics:** Dual-encoder contrastive language-image pretraining trained on 400M internet pairs.
* **Prompt Engineering:** Ensembles multiple domain-adapted prompts per category:
  * `"a photo of {food}, a traditional Indian street food dish"`
  * `"a delicious plate of Indian street food {food}"`
  * `"a street food vendor serving fresh {food} in India"`
* **Embeddings:** Text features are L2-normalized, averaged across templates, and projected against normalized image embeddings.
* **Explainability Notice:** Standard CNN Grad-CAM is structurally incompatible with Vision Transformer self-attention without specialized rollout/relevance propagation.

---

## 2. Training Hyperparameters & Regularization

* **Input Resolution:** 224x224 RGB.
* **Augmentations:** RandomResizedCrop (scale 0.75-1.0), RandomHorizontalFlip, RandomRotation(15°), ColorJitter (brightness 0.15, contrast 0.15, saturation 0.15).
* **Normalization:** ImageNet statistics ($\mu = [0.485, 0.456, 0.406]$, $\sigma = [0.229, 0.224, 0.225]$).
* **Loss Function:** Cross-Entropy Loss with label smoothing ($\epsilon = 0.10$) to prevent overconfident predictions on visually similar street foods.
* **Optimizers:** AdamW (weight decay $10^{-4}$, initial learning rate $10^{-4}$) or SGD with momentum (0.90).
* **Learning Rate Scheduler:** Cosine Annealing LR ($T_{max} = \text{epochs}$, $\eta_{min} = 10^{-6}$) or ReduceLROnPlateau.
* **Early Stopping:** Monitored on validation accuracy with patience of 5 epochs.

---

## 3. Out-of-Distribution & Unknown Food Detection

Softmax output vectors do not naturally provide calibrated confidence scores. StreetFoodAI implements a dual-gate rejection mechanism:

1. **Maximum Probability Threshold:** If $\max_c P(y = c | X) < \tau_{\text{conf}}$ (default 0.60), the image is flagged as uncertain.
2. **Shannon Entropy Threshold:** Uniform or flat probability spreads across multiple classes are detected via entropy:
   $$H(P) = -\sum_{i=1}^{K} P_i \ln(P_i)$$
   If $H(P) > \tau_{\text{entropy}}$ (default 1.60 nats), the prediction is flagged as ambiguous.
3. When flagged, the system displays top candidates with clear disclaimers and withholds nutritional values.
