"""
Benchmarking utility for inference latency, throughput, and hardware profiling.
"""
import time
import platform
import numpy as np
import torch
import torch.nn as nn

def measure_inference_latency(
    model: nn.Module,
    input_size: tuple = (1, 3, 224, 224),
    device: str = "cpu",
    warmup_runs: int = 10,
    test_runs: int = 50
) -> dict:
    """
    Measures latency using synchronized high-precision timing.
    """
    model.eval()
    dummy_input = torch.randn(*input_size, device=device)

    # Warmup runs
    with torch.no_grad():
        for _ in range(warmup_runs):
            _ = model(dummy_input)
            if device.startswith("cuda"):
                torch.cuda.synchronize()

    latencies_ms = []
    with torch.no_grad():
        for _ in range(test_runs):
            t_start = time.perf_counter()
            _ = model(dummy_input)
            if device.startswith("cuda"):
                torch.cuda.synchronize()
            t_end = time.perf_counter()
            latencies_ms.append((t_end - t_start) * 1000.0)

    latencies_ms = np.array(latencies_ms)
    mean_lat = float(np.mean(latencies_ms))
    p95_lat = float(np.percentile(latencies_ms, 95))
    min_lat = float(np.min(latencies_ms))
    max_lat = float(np.max(latencies_ms))
    throughput = round(1000.0 / mean_lat, 2) if mean_lat > 0 else 0.0

    # Model parameter count and disk size
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    return {
        "device": device,
        "hardware_processor": platform.processor() or platform.machine(),
        "python_version": platform.python_version(),
        "torch_version": torch.__version__,
        "mean_latency_ms": round(mean_lat, 2),
        "p95_latency_ms": round(p95_lat, 2),
        "min_latency_ms": round(min_lat, 2),
        "max_latency_ms": round(max_lat, 2),
        "throughput_fps": throughput,
        "total_parameters": total_params,
        "trainable_parameters": trainable_params,
        "model_param_size_mb": round((total_params * 4) / (1024 * 1024), 2)
    }
