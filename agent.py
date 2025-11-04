from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def explain_file(code: str, prob_ai: float, attribution: str) -> str:
    prompt = f"""
Eres un profesor experto en programación. Analiza este código Python.

Probabilidad IA: {round(prob_ai * 100, 1)}%
Atribución LLM: {attribution}

Explica en español, claro y educativo (máx 4 oraciones):
- ¿Por qué es probable que sea IA?
- ¿Qué patrones lo delatan?
- ¿Qué modelo lo generó?

Código:
{code[:3000]}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error con OpenAI: {str(e)}"
