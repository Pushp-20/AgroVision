from pathlib import Path
import json
from functools import lru_cache

import torch
from torch import nn
from torchvision import models, transforms
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / 'models' / 'agrovision_mobilenetv2.pth'
CLASSES_PATH = BASE_DIR / 'models' / 'class_names.json'
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

@lru_cache(maxsize=1)
def load_model():
    with open(CLASSES_PATH, 'r', encoding='utf-8') as f:
        class_names = json.load(f)
    if isinstance(class_names, dict):
        class_names = [class_names[str(i)] for i in range(len(class_names))]
    model = models.mobilenet_v2(weights=None)
    model.classifier[1] = nn.Linear(model.last_channel, len(class_names))
    checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=True)
    if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
        checkpoint = checkpoint['model_state_dict']
    model.load_state_dict(checkpoint)
    model = model.to(device)
    model.eval()
    return model, class_names

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def predict_all(image):
    model, class_names = load_model()
    if not isinstance(image, Image.Image):
        image = Image.open(image)
    tensor = transform(image.convert('RGB')).unsqueeze(0).to(device)
    with torch.inference_mode():
        scores = torch.softmax(model(tensor), dim=1)[0].cpu().tolist()
    return sorted(zip(class_names, [score * 100 for score in scores]), key=lambda x: x[1], reverse=True)

def predict_disease(image):
    return predict_all(image)[0]
