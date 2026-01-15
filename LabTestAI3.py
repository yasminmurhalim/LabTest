import streamlit as st
import torch
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image
import requests
import pandas as pd 

#Page Title
st.set_page_config(page_title="Computer Vision Classifier", layout="centered")
@st.cache_resource
def load_model():
  
    return models.resnet18(weights='DEFAULT').eval()

@st.cache_resource
def load_labels():
   
    url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
    return requests.get(url).text.splitlines()

model = load_model()
labels = load_labels()
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


img_file = st.camera_input("Take a photo of an object")

if img_file:
 
    img = Image.open(img_file).convert("RGB")
    batch = preprocess(img).unsqueeze(0)
    
    
    with torch.no_grad():
        out = model(batch)
        prob = F.softmax(out[0], dim=0)
        top5_p, top5_i = torch.topk(prob, 5)
    
  
    results = []
    for i in range(5):
        results.append({
            "Rank": i + 1,
            "Label": labels[top5_i[i]],
            "Probability": f"{top5_p[i].item():.2%}" # Formatted as percentage
        })
    
    st.subheader("Top 5 Predictions")
    st.table(pd.DataFrame(results))