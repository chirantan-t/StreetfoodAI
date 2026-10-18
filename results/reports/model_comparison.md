# StreetFoodAI: Model Architecture Comparison

| Architecture | Status | Accuracy | Macro F1 | Latency (ms) | Throughput (FPS) | Parameters (M) | Model Size (MB) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **mobilenet_v3_large** | Not evaluated (Untrained classification head) | Not evaluated | Not evaluated | 13.54 | 73.85 | 4.23 | 16.13 |
| **efficientnet_b0** | Not evaluated (Untrained classification head) | Not evaluated | Not evaluated | 21.15 | 47.29 | 4.03 | 15.39 |
| **clip** | Not evaluated (Requires test dataset) | Not evaluated | Not evaluated | 78.4 | 12.8 | 151.28 | 577.1 |

*Note: Where accuracy/F1 indicates 'Not evaluated', actual model fine-tuning on annotated food images is required. Latency and parameter sizes reflect authentic CPU hardware profiling.*