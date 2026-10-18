"""
Image transforms and data augmentation pipelines for StreetFoodAI.
Standardized resolution: 224x224 (compatible with MobileNetV3, EfficientNet-B0, CLIP).
"""
from torchvision import transforms

# Standard ImageNet normalization statistics
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

def get_train_transforms(image_size: int = 224):
    """
    Data augmentation for training Indian street food models:
    - Aspect-ratio preserving resize and random crop
    - Random horizontal flip
    - Color jitter for varying street lighting and frying oil shades
    - Random rotation for round plates/puris/bowls
    """
    resize_dim = int(image_size * 256 / 224)
    return transforms.Compose([
        transforms.Resize(resize_dim),
        transforms.RandomResizedCrop(image_size, scale=(0.7, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

def get_eval_transforms(image_size: int = 224):
    """
    Deterministic evaluation/inference transforms:
    - Resize smaller edge preserving aspect ratio, center crop, normalize
    """
    resize_dim = int(image_size * 256 / 224)
    return transforms.Compose([
        transforms.Resize(resize_dim),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

def get_raw_display_transforms(image_size: int = 224):
    """
    Transform for displaying original image alongside Grad-CAM
    """
    resize_dim = int(image_size * 256 / 224)
    return transforms.Compose([
        transforms.Resize(resize_dim),
        transforms.CenterCrop(image_size)
    ])
