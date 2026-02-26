from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
from config import LABELS, MODEL_NAME

label2id = {l: i for i, l in enumerate(LABELS)}
id2label = {i: l for l, i in label2id.items()}

def load_model():
    processor = LayoutLMv3Processor.from_pretrained(
        MODEL_NAME,
        apply_ocr=False
    )

    model = LayoutLMv3ForTokenClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(LABELS),
        id2label=id2label,
        label2id=label2id
    )

    return processor, model
