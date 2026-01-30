import torch
from torchvision import transforms
from PIL import Image

def load_model(model_path, device="cpu"):
    model = torch.load(model_path, map_location=device)
    model.eval()
    return model

transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406], [0.229,0.224,0.225])
])

def predict_disease(model, image_path, classes):
    img = Image.open(image_path).convert("RGB")
    img_t = transform(img).unsqueeze(0)
    with torch.no_grad():
        output = model(img_t)
        _, pred = torch.max(output, 1)
    return classes[pred.item()]
