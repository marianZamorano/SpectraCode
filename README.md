# 🧠 SpectraCode  
### Sistema de Detección de Código Generado por Inteligencia Artificial

[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

---

## 📘 Descripción general  

**SpectraCode** es una API web desarrollada en **Python 3.13** con **FastAPI**, diseñada para analizar repositorios Python comprimidos en formato `.zip` y determinar la probabilidad de que su código haya sido generado por Inteligencia Artificial.  

El sistema utiliza un **ensemble de modelos** que combina:  
- **Perplejidad (GPT-2)** para medir entropía textual.  
- **Análisis de sintaxis (AST)** para evaluar estructura y complejidad.  
- **Estilometría** para identificar patrones de estilo humano vs IA.  
- **CodeBERT** como clasificador profundo de secuencias de código.  

Además, genera **explicaciones educativas** en español mediante **GPT-4o** y puede aplicar **parches automáticos** a vulnerabilidades detectadas en el código.  

---

## 🧩 Funcionalidades principales  

- 🔍 Detección automática de código Python generado por IA.  
- 🧠 Ensemble de detectores (GPT-2, AST, Estilometría, CodeBERT).  
- 💬 Explicaciones interpretables en español generadas por GPT-4o.  
- 📚 Sistema de recuperación aumentada (RAG) con datasets públicos.  
- 📊 Exportación de resultados a `.xlsx` o `.csv`.  
- 🛡️ Identificación y parcheo de vulnerabilidades comunes.  
- 🐳 Arquitectura reproducible con Docker y Docker Compose.  

---

## ⚙️ Requisitos  

### Dependencias principales  

```txt
fastapi[standard]>=0.116.1
uvicorn[standard]>=0.24.0
openai>=1.30.0
python-dotenv>=1.0.0
langchain>=0.1.0
transformers>=4.36.0
torch>=2.1.0
numpy>=1.24.0
pydantic>=2.5.0
python-multipart>=0.0.6
watchfiles>=0.21.0
chromadb>=0.4.24
sentence-transformers>=2.2.2
tqdm>=4.66.0
scikit-learn>=1.3.0
websocket-client>=1.6.0
pandas>=2.0.0
pyarrow>=14.0.0
dotenv>=0.9.9
openpyxl>=3.1.5
```

### Requisitos del sistema

* **Python 3.13 o superior**
* **Docker y Docker Compose** (para entorno completo)
* Conexión a internet (para descarga de datasets del RAG)

---

## 🚀 Instalación local

### 1️⃣ Clona el repositorio

```bash
git clone https://github.com/<tu_usuario>/spectracode.git
cd spectracode
```

### 2️⃣ Crea el archivo `.env`

```bash
OPENAI_API_KEY=tu_clave_de_openai
```

### 3️⃣ Instala las dependencias

```bash
pip install -r requirements.txt
```

O si usas **uv** (recomendado):

```bash
uv pip install -e .
```

---

## ▶️ Ejecución del proyecto

### 🧩 Opción 1: Modo desarrollo local

Ejecuta el servidor FastAPI con:

```bash
uv run fastapi dev api.py
```

Esto iniciará el servidor en:

> 🌐 [http://localhost:8000/docs](http://localhost:8000/docs)

Desde ahí podrás subir un archivo `.zip` y ver el análisis interactivo.

---

### 🧩 Opción 2: Modo Docker

#### Construir los contenedores

```bash
docker-compose build
```

#### Levantar los servicios

```bash
docker-compose up
```

Esto iniciará:

* **spectracode-api** → API principal (puerto `8000`)
* **rag-builder** → construye la base RAG con datasets Python

> ⚠️ La primera ejecución puede tardar varios minutos mientras se descargan los datasets (MBPP, HumanEval-Pro, CodeSearchNet).

---

## 📚 Reconstruir la base RAG manualmente

Si deseas regenerar la base vectorial del sistema (por ejemplo, tras limpiar `data/rag_db/`):

```bash
python rag/build_rag.py
```

Esto descargará e indexará los datasets públicos en `data/rag_db/chroma`.

---

## 📊 Uso del analizador

### Paso 1. Comprime un repositorio Python

```bash
zip -r mi_proyecto.zip ./mi_proyecto/
```

### Paso 2. Envía el ZIP al endpoint `/analyze-repo`

```bash
curl -X POST "http://localhost:8000/analyze-repo" \
     -F "file=@mi_proyecto.zip" \
     -o resultados.xlsx
```

### Paso 3. Revisa los resultados

El archivo generado (`resultados.xlsx` o `.csv`) incluirá:

* `file` — nombre del archivo analizado
* `ai_probability` — probabilidad estimada de origen IA
* `perplexity_score`, `ast_score`, `codebert_score` — métricas internas
* `attribution` — valores ponderados por detector
* `explanation` — resumen educativo generado por GPT-4o

---

## 🧠 Evaluación del modelo

Para probar el rendimiento del ensemble con un ZIP de prueba:

```bash
python evaluate.py tests.zip
```

Se mostrará el **F1 Score** y el **classification report** (Human vs IA).

---

## 🛡️ Parches automáticos de seguridad

El módulo `utils/patcher.py` identifica y comenta vulnerabilidades comunes:

* `eval()`
* `os.system()`
* `subprocess.call()`
* `pickle.loads()`
* `input()`

Ejemplo de salida:

```python
# SECURE PATCH: eval() detected - INSECURE at line ~23
# eval("codigo")
```

---

## 📂 Estructura del proyecto

```
spectracode/
│
├── api.py                 # API principal (FastAPI)
├── agent.py               # Explicaciones GPT-4o
├── evaluate.py            # Evaluación del modelo
├── docker-compose.yaml    # Orquestación de servicios
├── Dockerfile             # Imagen Docker
├── .env                   # Variables de entorno
├── pyproject.toml         # Dependencias y configuración
│
├── /detectors/            # Módulos de detección
│   ├── ensemble.py
│   ├── perplexityScore.py
│   ├── stylometryModel.py
│   └── classifier.py
│
├── /utils/                # Utilidades y helpers
│   ├── astUtils.py
│   ├── patcher.py
│   └── zip_parser.py
│
├── /rag/                  # Recuperación aumentada (RAG)
│   ├── build_rag.py
│   └── query_rag.py
│
└── /data/rag_db/          # Base vectorial persistente
```

---

## 👩‍💻 Autora

**Marian Isabel Zamorano Alcázar**
Proyecto final — *Tópicos Selectos en Inteligencia Artificial (2025)*

---
