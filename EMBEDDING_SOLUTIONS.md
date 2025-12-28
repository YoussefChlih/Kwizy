# Vercel OOM Error Fix - Alternative Embeddings Guide

## Problem
Your Vercel build ran Out of Memory (OOM) because heavy ML libraries were being installed:
- `sentence-transformers` (~2GB)
- `scikit-learn` (~500MB)
- `chromadb` (large embeddings index)
- `numpy` (large dependency tree)

## Solution
Replace local embedding models with cloud-based embedding APIs. Here are your options:

---

## Option 1: Mistral AI Embeddings (Recommended - You Already Use This!)

Since you're already using Mistral, use their embeddings API:

```python
from mistralai.client import MistralClient
from mistralai.models.chat_message import ChatMessage

client = MistralClient(api_key=os.getenv('MISTRAL_API_KEY'))

def get_embeddings(text: str):
    """Get embeddings from Mistral API"""
    response = client.get_embeddings(
        model="mistral-embed",
        input=[text]
    )
    return response.data[0].embedding

# Usage
embedding = get_embeddings("Your text here")
# Returns list of floats
```

**Pros:**
- ✅ Same API key you already use
- ✅ No additional setup
- ✅ 1536-dimensional embeddings
- ✅ Cheap ($0.02 per million tokens)

**Integration:**
Update your `rag_system.py` to use Mistral embeddings instead of sentence-transformers.

---

## Option 2: OpenAI Embeddings

If you want to switch to OpenAI:

```bash
pip install openai
```

```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_embeddings(text: str):
    """Get embeddings from OpenAI"""
    response = client.embeddings.create(
        model="text-embedding-3-small",  # Lightweight model
        input=text
    )
    return response.data[0].embedding
```

**Pros:**
- ✅ Very reliable
- ✅ High quality embeddings
- ✅ Cheap: $0.02 per 1M input tokens

**Environment Variable:**
```
OPENAI_API_KEY=sk-...
```

---

## Option 3: Cohere Embeddings

```bash
pip install cohere
```

```python
import cohere

co = cohere.Client(api_key=os.getenv('COHERE_API_KEY'))

def get_embeddings(text: str):
    """Get embeddings from Cohere"""
    response = co.embed(texts=[text], model="embed-english-light-v3.0")
    return response.embeddings[0]
```

**Pros:**
- ✅ Lightweight models available
- ✅ Free tier available
- ✅ Good for multilingual

---

## Option 4: Use Supabase pgvector

Store embeddings in PostgreSQL with pgvector extension:

```python
from sqlalchemy import text

def store_embedding(content: str, embedding: list):
    """Store text and embedding in Supabase"""
    query = text("""
        INSERT INTO documents (content, embedding)
        VALUES (:content, :embedding::vector)
    """)
    db.session.execute(query, {
        'content': content,
        'embedding': embedding
    })
    db.session.commit()

def similarity_search(query_embedding: list, limit: int = 10):
    """Find similar documents"""
    query = text("""
        SELECT content, 1 - (embedding <=> :embedding::vector) as similarity
        FROM documents
        ORDER BY embedding <=> :embedding::vector
        LIMIT :limit
    """)
    results = db.session.execute(query, {
        'embedding': query_embedding,
        'limit': limit
    })
    return results.fetchall()
```

**Setup (one-time):**
```sql
-- Enable pgvector extension in Supabase
CREATE EXTENSION vector;

-- Create documents table
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for faster search
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

## Implementation Steps

### Step 1: Choose Your Solution
- **Easiest**: Option 1 (Mistral Embeddings)
- **Most Reliable**: Option 2 (OpenAI)
- **Best Value**: Option 3 (Cohere) or Option 4 (Supabase)

### Step 2: Update Environment Variables
Add to Vercel dashboard (if needed):
```
# For Option 1 - Already have this!
MISTRAL_API_KEY=xxx

# For Option 2
OPENAI_API_KEY=xxx

# For Option 3
COHERE_API_KEY=xxx

# Database (for Option 4)
DATABASE_URL=postgresql://...
```

### Step 3: Update `rag_system.py`
Replace all `sentence-transformers` imports with your chosen API:

```python
# OLD (remove)
# from sentence_transformers import SentenceTransformer
# model = SentenceTransformer('all-MiniLM-L6-v2')

# NEW (add)
from mistralai.client import MistralClient
mistral_client = MistralClient(api_key=os.getenv('MISTRAL_API_KEY'))

def get_query_embedding(query: str):
    """Get embedding from Mistral API"""
    response = mistral_client.get_embeddings(
        model="mistral-embed",
        input=[query]
    )
    return response.data[0].embedding
```

### Step 4: Update Vector Storage
Replace ChromaDB with PostgreSQL/Supabase or cloud vector DB:

```python
# Option A: PostgreSQL with pgvector (recommended for you)
from sqlalchemy.dialects.postgresql import JSON

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    embedding = db.Column(JSON)  # Store as JSON
    metadata = db.Column(JSON)

# Option B: Use cloud vector database
# from pinecone import Pinecone
# pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
```

### Step 5: Deploy
```bash
git add .
git commit -m "Replace local embeddings with cloud API"
git push origin main
```

Vercel will build successfully without memory issues! ✅

---

## Cost Comparison

| Option | Cost | Pros | Cons |
|--------|------|------|------|
| Mistral Embeddings | $0.02/1M tokens | Already configured | Depends on Mistral availability |
| OpenAI | $0.02/1M tokens | Very reliable | Need API key |
| Cohere | Free tier | Good quality | Need API key |
| Supabase pgvector | $25/month starter | No extra costs once configured | Needs PostgreSQL |
| Pinecone | $0.04/1M vectors | Dedicated vector DB | Monthly cost |

---

## Testing Locally

To test with local embeddings before deploying:

```bash
# Install optional dependencies
pip install -r requirements-optional.txt

# Run locally
python app.py
```

For Vercel, make sure to use cloud embeddings!

---

## Next Steps

1. ✅ **Done:** Removed heavy dependencies from requirements.txt
2. **TODO:** Choose an embedding solution from above
3. **TODO:** Update `rag_system.py` with chosen API
4. **TODO:** Test locally
5. **TODO:** Commit and push
6. **TODO:** Deploy to Vercel

---

## Questions?

- Mistral docs: https://docs.mistral.ai/capabilities/embeddings/
- OpenAI docs: https://platform.openai.com/docs/guides/embeddings
- Supabase pgvector: https://supabase.com/docs/guides/database/extensions/pgvector
