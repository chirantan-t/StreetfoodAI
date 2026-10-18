"""
ONNX Model Export utility for StreetFoodAI.
Enables cross-platform deployment on edge runtimes (ONNX Runtime, WebAssembly, mobile).
"""
import sys
from pathlib import Path
import torch

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.models.registry import get_model

def export_to_onnx(
    model_name: str = "mobilenet_v3_large",
    weights_path: str = None,
    output_path: str = "models/checkpoints/streetfood_model.onnx",
    num_classes: int = 20,
    opset_version: int = 14
) -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    print(f"Exporting {model_name} to ONNX format at {output_path}...")

    model, meta = get_model(
        arch_name=model_name,
        num_classes=num_classes,
        weights_path=weights_path,
        pretrained=True,
        device="cpu"
    )
    model.eval()

    dummy_input = torch.randn(1, 3, 224, 224, requires_grad=False)

    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=opset_version,
        do_constant_folding=True,
        dynamo=False,
        input_names=["input_image"],
        output_names=["logits"],
        dynamic_axes={
            "input_image": {0: "batch_size"},
            "logits": {0: "batch_size"}
        }
    )

    print(f"ONNX export succeeded. Model saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export StreetFoodAI model to ONNX")
    parser.add_argument("--model", default="mobilenet_v3_large", choices=["mobilenet_v3_large", "efficientnet_b0"])
    parser.add_argument("--weights", default=None)
    parser.add_argument("--output", default="models/checkpoints/streetfood_model.onnx")
    args = parser.parse_args()

    export_to_onnx(args.model, args.weights, args.output)
