# Local RAG Agent

A fully offline RAG (Retrieval-Augmented Generation) based question-answering assistant developed using Foundry Local.

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

## Resources I used during the RAG assistant setup phase (Microsoft Summer AI Innovation Bootcamp):
XX https://techcommunity.microsoft.com/blog/azuredevcommunityblog/building-your-first-local-rag-application-with-foundry-local/4501968

XX https://learn.microsoft.com/en-us/azure/foundry-local/what-is-foundry-local 

XX https://learn.microsoft.com/en-us/azure/foundry-local/tutorials/tutorial-build-rag-app?tabs=windows 

XX https://sqlite.org/index.html 

XX https://azurefeeds.com/2026/03/30/building-your-first-local-rag-application-with-foundry-local/ 

XX https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/prompt-engineering 

XX https://learn.microsoft.com/en-us/windows/apps/develop/data-access/sqlite-data-access
