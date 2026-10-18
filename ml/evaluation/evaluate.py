"""
Model Evaluation Pipeline for StreetFoodAI.
Computes multi-class metrics, confusion matrix, per-class statistics,
and generates publication-quality visualization charts.
"""
import os
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)
import torch
from torch.utils.data import DataLoader

from ml.data.dataset import StreetFoodDataset
from ml.data.augmentation import get_eval_transforms
from ml.models.registry import get_model, load_classes_config
from ml.evaluation.latency import measure_inference_latency

def evaluate_model(
    model_name: str = "mobilenet_v3_large",
    weights_path: str = None,
    test_dir: str = "data/processed/test",
    classes_config_path: str = "ml/config/classes.json",
    results_dir: str = "results",
    batch_size: int = 32
) -> Dict[str, Any]:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\nEvaluating model: {model_name} on device: {device}")

    classes_cfg = load_classes_config(classes_config_path)
    classes = classes_cfg["classes"]
    num_classes = len(classes)

    test_path = Path(test_dir)
    if not test_path.exists() or len(list(test_path.glob("*/*.*"))) == 0:
        print(f"Notice: Test set at '{test_dir}' is empty or does not exist.")
        print("To evaluate on real test data, run dataset preparation and model training.")
        return {
            "model_name": model_name,
            "status": "not_evaluated",
            "message": f"No test dataset found in {test_dir}"
        }

    test_dataset = StreetFoodDataset(
        root_dir=str(test_path),
        transform=get_eval_transforms(),
        classes_config_path=classes_config_path
    )
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    model, meta = get_model(
        arch_name=model_name,
        num_classes=num_classes,
        weights_path=weights_path,
        pretrained=True,
        device=str(device)
    )

    y_true: List[int] = []
    y_pred: List[int] = []
    y_probs: List[np.ndarray] = []

    model.eval()
    with torch.no_grad():
        for images, labels, _ in test_loader:
            images = images.to(device)
            outputs = model(images)
            probs = torch.softmax(outputs, dim=-1).cpu().numpy()
            preds = np.argmax(probs, axis=1)

            y_true.extend(labels.numpy().tolist())
            y_pred.extend(preds.tolist())
            y_probs.extend(probs)

    y_true_np = np.array(y_true)
    y_pred_np = np.array(y_pred)

    # Core Metrics
    acc = float(accuracy_score(y_true_np, y_pred_np))
    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
        y_true_np, y_pred_np, average="macro", zero_division=0
    )
    precision_per_cls, recall_per_cls, f1_per_cls, support_per_cls = precision_recall_fscore_support(
        y_true_np, y_pred_np, average=None, labels=list(range(num_classes)), zero_division=0
    )

    cm = confusion_matrix(y_true_np, y_pred_np, labels=list(range(num_classes)))

    # Latency & Hardware Benchmarks
    benchmarks = measure_inference_latency(model, device=str(device))

    per_class_results = {}
    for i, cls_name in enumerate(classes):
        per_class_results[cls_name] = {
            "precision": round(float(precision_per_cls[i]), 4),
            "recall": round(float(recall_per_cls[i]), 4),
            "f1_score": round(float(f1_per_cls[i]), 4),
            "support": int(support_per_cls[i])
        }

    report = {
        "model_name": model_name,
        "weights_path": weights_path,
        "weights_status": meta["status"],
        "num_test_samples": len(test_dataset),
        "overall_accuracy": round(acc, 4),
        "macro_precision": round(float(precision_macro), 4),
        "macro_recall": round(float(recall_macro), 4),
        "macro_f1": round(float(f1_macro), 4),
        "per_class": per_class_results,
        "confusion_matrix": cm.tolist(),
        "benchmarks": benchmarks
    }

    # Save outputs
    res_dir = Path(results_dir)
    eval_dir = res_dir / "evaluations"
    plots_dir = res_dir / "plots"
    eval_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)

    report_path = eval_dir / f"{model_name}_evaluation.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Confusion matrix plot
    plt.figure(figsize=(14, 12))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Oranges",
        xticklabels=classes,
        yticklabels=classes
    )
    plt.title(f"Confusion Matrix - {model_name} (Acc: {acc*100:.1f}%)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Predicted Class", fontsize=11)
    plt.ylabel("True Class", fontsize=11)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    cm_path = plots_dir / f"{model_name}_confusion_matrix.png"
    plt.savefig(cm_path, dpi=300)
    plt.close()

    # Per-class F1 bar chart
    plt.figure(figsize=(14, 6))
    f1_vals = [per_class_results[c]["f1_score"] for c in classes]
    bars = plt.bar(range(len(classes)), f1_vals, color="#f97316", edgecolor="#c2410c")
    plt.xticks(range(len(classes)), classes, rotation=45, ha="right", fontsize=9)
    plt.ylim(0, 1.05)
    plt.title(f"Per-Class F1-Scores - {model_name} (Macro F1: {f1_macro:.3f})", fontsize=14, fontweight="bold")
    plt.ylabel("F1 Score", fontsize=11)
    plt.axhline(f1_macro, color="red", linestyle="--", label=f"Macro Avg: {f1_macro:.3f}")
    plt.legend()
    plt.tight_layout()
    f1_path = plots_dir / f"{model_name}_per_class_f1.png"
    plt.savefig(f1_path, dpi=300)
    plt.close()

    print(f"\nEvaluation Complete:")
    print(f"- Overall Accuracy: {acc*100:.2f}%")
    print(f"- Macro F1-Score: {f1_macro:.4f}")
    print(f"- Mean Latency: {benchmarks['mean_latency_ms']} ms ({benchmarks['throughput_fps']} fps)")
    print(f"- Report saved to: {report_path}")
    print(f"- Heatmap saved to: {cm_path}")

    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="StreetFoodAI Model Evaluation")
    parser.add_argument("--model", default="mobilenet_v3_large", choices=["mobilenet_v3_large", "efficientnet_b0"])
    parser.add_argument("--weights", default=None, help="Path to model checkpoint")
    parser.add_argument("--test-dir", default="data/processed/test")
    parser.add_argument("--results-dir", default="results")
    args = parser.parse_args()

    evaluate_model(
        model_name=args.model,
        weights_path=args.weights,
        test_dir=args.test_dir,
        results_dir=args.results_dir
    )
