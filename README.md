# Local RAG Agent

A fully offline RAG (Retrieval-Augmented Generation) based question-answering assistant developed using Foundry Local.
NOTE:To understand the logic behind creating a local agent, I first made the source and interface languages Turkish, I will later translate them to English.
## Features
- Fully offline operation with local LLM (phi-3.5-mini)
- SQLite-based embedding storage
- CLI and Streamlit web interface

## Installation
\`\`\`
pip install -r requirements.txt
\`\`\`

## Running
For CLI:
\`\`\`
python main.py
\`\`\`

For the web interface:
\`\`\`
python -m streamlit run app.py
\`\`\`
