import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import math

class PerplexityDetector:
    def __init__(self):
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        self.model = GPT2LMHeadModel.from_pretrained("gpt2")
        self.model.eval()
    
    def get_score(self, code: str) -> float:
        try:
            inputs = self.tokenizer(code, return_tensors="pt", truncation=True, max_length=1024)
            with torch.no_grad():
                outputs = self.model(**inputs, labels=inputs["input_ids"])
                loss = outputs.loss
            ppl = math.exp(loss.item())
            # Normalizar: <50 = humano, >100 = IA
            return min(ppl / 200.0, 1.0)
        except:
            return 0.5