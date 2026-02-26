from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)
model.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def embed(text: str) -> np.ndarray:
    if not text.strip():
        return np.zeros(384)

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs)

    embeddings = outputs.last_hidden_state.mean(dim=1)
    vec = embeddings[0].cpu().numpy()

    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec
