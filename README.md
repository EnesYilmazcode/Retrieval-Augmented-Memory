# Retrieval-Augmented-Memory

instead of stuffing the entire chat history into the prompt (which eats up the context window), this uses chromadb to store messages as vectors and retrieves only the relevant ones when needed.

uses streamlit for a simple chat ui.

![example](images/exampel.png)

## how it works

1. user sends a message
2. we search chromadb for semantically similar past messages
3. only those relevant messages get sent to the llm as context
4. response gets saved back to chromadb for future retrieval

## setup

```
pip install -r requirements.txt
```

create a `.env` file:
```
GOOGLE_API_KEY=your_key_here
```

run it:
```
python -m streamlit run app.py
```

first run will download the embedding model (~80mb), after that its cached.
