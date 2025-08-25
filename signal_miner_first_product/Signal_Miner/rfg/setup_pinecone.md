# Pinecone Setup for GrowthSignal RAG

This guide covers setting up Pinecone for vector storage in the GrowthSignal RAG system, with fallback to local FAISS.

## Quick Start

### 1. Create Pinecone Account
1. Go to [pinecone.io](https://pinecone.io)
2. Sign up for a free account
3. Get your API key from the console

### 2. Create Index
```bash
# Install Pinecone client
pip install pinecone-client

# Create the index (run once)
python -c "
import pinecone
pinecone.init(api_key='YOUR_API_KEY', environment='YOUR_ENV')
pinecone.create_index(
    name='astra-signals-dev',
    dimension=1536,  # text-embedding-3-small dimension
    metric='cosine'
)
print('Index created successfully!')
"
```

### 3. Set Environment Variables
```bash
# Required
export PINECONE_API_KEY="your_pinecone_api_key"
export PINECONE_ENV="your_environment"  # e.g., "us-east-1-aws"

# Optional: Override index name
export PINECONE_INDEX_NAME="astra-signals-dev"
```

## Detailed Setup

### Index Configuration
- **Name**: `astra-signals-dev`
- **Dimension**: 1536 (for `text-embedding-3-small`)
- **Metric**: `cosine` (recommended for text embeddings)
- **Environment**: Choose closest to your location

### Environment Variables
```bash
# Required for Pinecone
PINECONE_API_KEY=your_api_key_here
PINECONE_ENV=your_environment_here

# Optional overrides
PINECONE_INDEX_NAME=astra-signals-dev  # default
```

### Example Commands

#### Create Index
```python
import pinecone

# Initialize
pinecone.init(api_key='YOUR_API_KEY', environment='YOUR_ENV')

# Create index
pinecone.create_index(
    name='astra-signals-dev',
    dimension=1536,
    metric='cosine'
)
```

#### Test Connection
```python
import pinecone

# Initialize
pinecone.init(api_key='YOUR_API_KEY', environment='YOUR_ENV')

# Get index
index = pinecone.Index('astra-signals-dev')

# Test with dummy vector
test_vector = [0.1] * 1536
index.upsert(vectors=[('test', test_vector, {'text': 'test'})])
print("✅ Pinecone connection successful!")
```

#### Manual Upsert Example
```python
from rfg.pinecone_helper import get_store

# Get store (will use Pinecone if env vars are set)
store = get_store(embed_dim=1536, index_name="astra-signals-dev")

# Prepare vectors
vectors = [
    ("doc1", [0.1, 0.2, ...], {"text": "Sample text 1", "domain": "example.com"}),
    ("doc2", [0.3, 0.4, ...], {"text": "Sample text 2", "domain": "example.com"})
]

# Upsert
store.upsert(vectors)
print("✅ Vectors upserted successfully!")
```

#### Manual Query Example
```python
from rfg.pinecone_helper import get_store

# Get store
store = get_store(embed_dim=1536, index_name="astra-signals-dev")

# Query vector
query_vector = [0.1] * 1536

# Search
results = store.query(query_vector, top_k=5)
for result in results:
    print(f"Score: {result['score']:.3f}, Text: {result['text'][:100]}...")
```

## FAISS Fallback

If Pinecone is not available, the system automatically falls back to local FAISS storage.

### Installation
```bash
# For most systems
pip install faiss-cpu

# For Windows
pip install faiss-cpu==1.7.4
```

### Usage
```python
# No environment variables needed - automatically uses FAISS
from rfg.pinecone_helper import get_store

# This will use FAISS if PINECONE_API_KEY is not set
store = get_store(embed_dim=1536)

# Same interface as Pinecone
vectors = [
    ("doc1", [0.1, 0.2, ...], {"text": "Sample text 1"}),
    ("doc2", [0.3, 0.4, ...], {"text": "Sample text 2"})
]

store.upsert(vectors)
results = store.query([0.1] * 1536, top_k=5)
```

### FAISS vs Pinecone

| Feature | Pinecone | FAISS |
|---------|----------|-------|
| **Storage** | Cloud | Local |
| **Scalability** | Unlimited | Limited by RAM |
| **Persistence** | Yes | No (in-memory) |
| **Setup** | Account + API key | pip install |
| **Cost** | Free tier available | Free |
| **Performance** | Fast | Very fast |

## Troubleshooting

### Common Issues

#### 1. Index Not Found
```bash
# Error: Index 'astra-signals-dev' not found
# Solution: Create the index first
python -c "
import pinecone
pinecone.init(api_key='YOUR_API_KEY', environment='YOUR_ENV')
pinecone.create_index('astra-signals-dev', dimension=1536, metric='cosine')
"
```

#### 2. Wrong Dimension
```bash
# Error: Vector dimension mismatch
# Solution: Use 1536 for text-embedding-3-small
# Check your embedding model dimension
```

#### 3. Environment Variable Issues
```bash
# Check if variables are set
echo $PINECONE_API_KEY
echo $PINECONE_ENV

# Set them if missing
export PINECONE_API_KEY="your_key"
export PINECONE_ENV="your_env"
```

#### 4. FAISS Installation Issues
```bash
# Windows: Use specific version
pip install faiss-cpu==1.7.4

# Linux/Mac: Use latest
pip install faiss-cpu

# Alternative: Use conda
conda install -c conda-forge faiss-cpu
```

### Testing Your Setup

#### Test Pinecone
```bash
# Set environment variables
export PINECONE_API_KEY="your_key"
export PINECONE_ENV="your_env"

# Run test
python -c "
from rfg.pinecone_helper import get_store
store = get_store(embed_dim=1536)
print('✅ Pinecone setup working!')
"
```

#### Test FAISS Fallback
```bash
# Unset Pinecone variables
unset PINECONE_API_KEY
unset PINECONE_ENV

# Run test
python -c "
from rfg.pinecone_helper import get_store
store = get_store(embed_dim=1536)
print('✅ FAISS fallback working!')
"
```

## Integration with GrowthSignal

### In generate_pack.py
The system automatically chooses between Pinecone and FAISS:

```python
# If PINECONE_API_KEY is set, uses Pinecone
# Otherwise, falls back to FAISS
store = get_store(embed_dim=dim, index_name="astra-signals-dev")
```

### In Streamlit UI
The UI works with both storage backends transparently:

```python
# No changes needed in UI code
# Storage choice is automatic based on environment variables
```

## Performance Tips

### Pinecone
- Use batch operations for multiple vectors
- Monitor your free tier usage
- Choose the closest environment to your location

### FAISS
- FAISS is very fast for local operations
- Memory usage scales with vector count
- Consider persisting vectors to disk for large datasets

## Next Steps

1. **Test your setup** with the examples above
2. **Run the signal miner** to generate embeddings
3. **Use the Streamlit UI** to test the full workflow
4. **Monitor performance** and adjust as needed

For more information, see the main [README.md](../README.md) and [rfg/README.md](README.md).
