"""
Training & Fine-Tuning Pipeline for StreetFoodAI.
Supports MobileNetV3-Large and EfficientNet-B0.
Features:
- Checkpointing and resuming interrupted runs
- Early stopping & LR scheduling
- Metrics tracking & MLflow experiment logging
- Class mappings and preprocessing metadata bundling
"""
import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, Any

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim import AdamW, SGD
from torch.optim.lr_scheduler import CosineAnnealingLR, ReduceLROnPlateau

from ml.data.dataset import StreetFoodDataset
from ml.data.augmentation import get_train_transforms, get_eval_transforms
from ml.models.registry import get_model, load_classes_config
from ml.training.early_stopping import EarlyStopping

def train_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels, _ in dataloader:
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        _, preds = torch.max(outputs, 1)
        correct += torch.sum(preds == labels.data).item()
        total += labels.size(0)

    epoch_loss = running_loss / max(total, 1)
    epoch_acc = correct / max(total, 1)
    return epoch_loss, epoch_acc

def evaluate_epoch(model, dataloader, criterion, device):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels, _ in dataloader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            correct += torch.sum(preds == labels.data).item()
            total += labels.size(0)

    epoch_loss = running_loss / max(total, 1)
    epoch_acc = correct / max(total, 1)
    return epoch_loss, epoch_acc

def run_training(
    model_name: str = "mobilenet_v3_large",
    data_dir: str = "data/processed",
    epochs: int = 25,
    batch_size: int = 32,
    lr: float = 1e-4,
    weight_decay: float = 1e-4,
    optimizer_type: str = "adamw",
    scheduler_type: str = "cosine",
    patience: int = 6,
    freeze_backbone: bool = False,
    checkpoints_dir: str = "ml/checkpoints",
    classes_config_path: str = "ml/config/classes.json",
    resume_checkpoint: str = None,
    use_mlflow: bool = True
) -> Dict[str, Any]:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cpu":
        torch.set_num_threads(2)
    print(f"\n==========================================")
    print(f"StreetFoodAI Training Pipeline")
    print(f"Model: {model_name} | Device: {device}")
    print(f"Data directory: {data_dir}")
    print(f"==========================================\n")

    train_path = Path(data_dir) / "train"
    val_path = Path(data_dir) / "val"

    if not train_path.exists() or len(list(train_path.glob("*/*.*"))) == 0:
        print(f"Error: No processed training images found in '{train_path}'.")
        print("Please place category images in 'data/raw/<Class_Name>' and execute:")
        print("  python scripts/prepare_data.py")
        return {"status": "error", "message": "Missing training data"}

    classes_cfg = load_classes_config(classes_config_path)
    num_classes = len(classes_cfg["classes"])

    # Datasets and Loaders
    train_dataset = StreetFoodDataset(
        root_dir=str(train_path),
        transform=get_train_transforms(),
        classes_config_path=classes_config_path
    )
    val_dataset = StreetFoodDataset(
        root_dir=str(val_path),
        transform=get_eval_transforms(),
        classes_config_path=classes_config_path
    )

    print(f"Train samples: {len(train_dataset)} | Val samples: {len(val_dataset)}")
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    # Build model
    model, _ = get_model(
        arch_name=model_name,
        num_classes=num_classes,
        pretrained=True,
        freeze_backbone=freeze_backbone,
        device=str(device)
    )

    # Loss function with slight label smoothing for generalization
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)

    # Optimizer with differential learning rate for fine-tuning feature backbone vs classification head
    if not freeze_backbone and hasattr(model, "base_model") and hasattr(model.base_model, "features"):
        optimizer_grouped_parameters = [
            {"params": [p for p in model.base_model.features.parameters() if p.requires_grad], "lr": lr * 0.2},
            {"params": [p for p in model.base_model.classifier.parameters() if p.requires_grad], "lr": lr}
        ]
        optimizer = AdamW(optimizer_grouped_parameters, weight_decay=weight_decay)
        print(f"Configured differential learning rates: backbone={lr * 0.2:.2e}, head={lr:.2e}")
    else:
        trainable_params = [p for p in model.parameters() if p.requires_grad]
        print(f"Trainable parameter tensors: {len(trainable_params)}")
        if optimizer_type.lower() == "sgd":
            optimizer = SGD(trainable_params, lr=lr, momentum=0.9, weight_decay=weight_decay)
        else:
            optimizer = AdamW(trainable_params, lr=lr, weight_decay=weight_decay)

    # Scheduler
    if scheduler_type == "plateau":
        scheduler = ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=2)
    else:
        scheduler = CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-6)

    # Checkpoints directory
    ckpt_dir = Path(checkpoints_dir)
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    best_model_path = ckpt_dir / f"best_{model_name}.pth"
    last_checkpoint_path = ckpt_dir / f"last_{model_name}.pth"

    start_epoch = 0
    best_val_acc = 0.0
    history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}

    # Resume from checkpoint if provided
    if resume_checkpoint and os.path.exists(resume_checkpoint):
        print(f"Resuming training from checkpoint: {resume_checkpoint}")
        ckpt = torch.load(resume_checkpoint, map_location=device)
        model.load_state_dict(ckpt["state_dict"])
        try:
            optimizer.load_state_dict(ckpt["optimizer_state_dict"])
        except Exception:
            print("Note: Fresh optimizer state initialized for unfreezing / fine-tuning.")
        if not freeze_backbone:
            start_epoch = 0
            best_val_acc = 0.0
        else:
            start_epoch = ckpt.get("epoch", 0) + 1
            best_val_acc = ckpt.get("best_val_acc", 0.0)
        history = ckpt.get("history", history)

    early_stopping = EarlyStopping(patience=patience, mode="max")

    # MLflow Setup
    mlflow_active = False
    if use_mlflow:
        try:
            import mlflow
            mlflow.set_experiment("StreetFoodAI_Recognition")
            mlflow.start_run(run_name=f"{model_name}_{int(time.time())}")
            mlflow.log_params({
                "model": model_name,
                "epochs": epochs,
                "batch_size": batch_size,
                "learning_rate": lr,
                "optimizer": optimizer_type,
                "weight_decay": weight_decay,
                "scheduler": scheduler_type,
                "num_classes": num_classes,
                "device": str(device)
            })
            mlflow_active = True
        except Exception as e:
            print(f"MLflow initialization skipped: {e}")

    # Training Loop
    for epoch in range(start_epoch, epochs):
        t0 = time.time()
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = evaluate_epoch(model, val_loader, criterion, device)

        if scheduler_type == "plateau":
            scheduler.step(val_acc)
        else:
            scheduler.step()

        elapsed = time.time() - t0

        history["train_loss"].append(round(train_loss, 4))
        history["train_acc"].append(round(train_acc, 4))
        history["val_loss"].append(round(val_loss, 4))
        history["val_acc"].append(round(val_acc, 4))

        print(f"Epoch [{epoch+1:02d}/{epochs:02d}] ({elapsed:.1f}s) | "
              f"Train Loss: {train_loss:.4f} Acc: {train_acc*100:.2f}% | "
              f"Val Loss: {val_loss:.4f} Acc: {val_acc*100:.2f}%")

        if mlflow_active:
            import mlflow
            mlflow.log_metrics({
                "train_loss": train_loss,
                "train_acc": train_acc,
                "val_loss": val_loss,
                "val_acc": val_acc,
                "lr": optimizer.param_groups[0]["lr"]
            }, step=epoch+1)

        # Save latest checkpoint
        checkpoint_data = {
            "epoch": epoch,
            "architecture": model_name,
            "state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "best_val_acc": best_val_acc,
            "history": history,
            "classes": classes_cfg["classes"],
            "preprocessing": {"image_size": 224, "mean": [0.485, 0.456, 0.406], "std": [0.229, 0.224, 0.225]}
        }
        torch.save(checkpoint_data, last_checkpoint_path)

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            checkpoint_data["best_val_acc"] = best_val_acc
            torch.save(checkpoint_data, best_model_path)
            print(f"  --> Saved new best checkpoint to {best_model_path} (Val Acc: {best_val_acc*100:.2f}%)")

        # Early stopping check
        if early_stopping(val_acc):
            print(f"Early stopping triggered at epoch {epoch+1}.")
            break

    # Save training history JSON
    history_file = ckpt_dir / f"{model_name}_history.json"
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    if mlflow_active:
        import mlflow
        mlflow.log_artifact(str(best_model_path))
        mlflow.log_artifact(str(history_file))
        mlflow.end_run()

    print(f"\nTraining finished. Best Val Acc: {best_val_acc*100:.2f}%")
    return {"status": "success", "best_val_acc": best_val_acc, "history": history}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="StreetFoodAI Training")
    parser.add_argument("--model", default="mobilenet_v3_large", choices=["mobilenet_v3_large", "efficientnet_b0"])
    parser.add_argument("--data-dir", default="data/processed")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--optimizer", default="adamw", choices=["adamw", "sgd"])
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--resume", default=None)
    parser.add_argument("--freeze-backbone", action="store_true", help="Freeze feature backbone for transfer learning")
    parser.add_argument("--no-mlflow", action="store_true")
    args = parser.parse_args()

    run_training(
        model_name=args.model,
        data_dir=args.data_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        optimizer_type=args.optimizer,
        patience=args.patience,
        freeze_backbone=args.freeze_backbone,
        resume_checkpoint=args.resume,
        use_mlflow=not args.no_mlflow
    )
