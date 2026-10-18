# Model Checkpoints & Pre-trained Weights

This directory stores fine-tuned PyTorch model weights (`.pth`) for StreetFoodAI.

## Architecture Support
- **MobileNetV3-Large** (Primary Edge Vision Backbone, 20 classes)
- **EfficientNet-B0** (Benchmark High-Accuracy Backbone)

## Weight Files
Binary weight checkpoints (`*.pth`) are excluded from Git version control to prevent repository bloat (>50 MB).

To train or reproduce weights locally:
```bash
python -m ml.training.train --model mobilenet_v3_large --epochs 15 --batch-size 16 --lr 1e-4
```

Checkpoint history and validation metrics are tracked in `mobilenet_v3_large_history.json`.
