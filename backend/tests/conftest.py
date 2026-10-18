import torch

# Cap PyTorch CPU threads to prevent Windows RAM allocation failures in low-memory environments
torch.set_num_threads(2)
