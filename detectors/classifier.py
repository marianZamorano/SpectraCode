from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class CodeBERTClassifier:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        self.model = AutoModelForSequenceClassification.from_pretrained("microsoft/codebert-base")
        self.model.eval()
    
    def predict_proba(self, code: str) -> float:
        try:
            inputs = self.tokenizer(code, return_tensors="pt", truncation=True, max_length=512)
            with torch.no_grad():
                logits = self.model(**inputs).logits
                prob = torch.softmax(logits, dim=1)[0][1].item()
            return prob
        except:
            return 0.5