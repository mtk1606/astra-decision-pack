# RAG Module - Decision Pack Generation

The RAG (Retrieval-Augmented Generation) module automatically generates Decision Packs from mined signals using OpenAI embeddings and vector search.

## Quick Start

### Prerequisites
```bash
# Install dependencies
pip install -r ../requirements.txt

# Set OpenAI API key (required)
export OPENAI_API_KEY="your_openai_api_key"
```

### Basic Usage
```bash
# Generate Decision Pack from latest signals
python generate_pack.py

# Specify input file
python generate_pack.py --input ../output/signals.json

# Use different models
python generate_pack.py --model gpt-4o-mini --embed_model text-embedding-3-small
```

## Storage Options

### Option 1: Pinecone (Recommended for Production)
```bash
# Set Pinecone credentials
export PINECONE_API_KEY="your_pinecone_key"
export PINECONE_ENV="your_environment"

# Create index (run once)
python -c "
import pinecone
pinecone.init(api_key='$PINECONE_API_KEY', environment='$PINECONE_ENV')
pinecone.create_index('astra-signals-dev', dimension=1536, metric='cosine')
"

# Run generator
python generate_pack.py
```

### Option 2: Local FAISS (Default Fallback)
```bash
# No additional setup needed - automatically uses FAISS
python generate_pack.py
```

## Command Line Options

```bash
python generate_pack.py [OPTIONS]

Options:
  --input PATH           Path to signals.json (default: latest output/signals.json)
  --outdir PATH          Output directory for Decision Packs (default: output/decision_packs)
  --embed_model MODEL    Embedding model (default: text-embedding-3-small)
  --model MODEL          LLM model (default: gpt-4o-mini)
  --index NAME           Pinecone index name (default: astra-signals-dev)
  --help                 Show help message
```

## Examples

### Generate from Specific File
```bash
python generate_pack.py --input ../output/techcrunch.com.json
```

### Use Different Models
```bash
# Use GPT-4 for better quality (more expensive)
python generate_pack.py --model gpt-4

# Use different embedding model
python generate_pack.py --embed_model text-embedding-ada-002
```

### Custom Output Directory
```bash
python generate_pack.py --outdir ../output/my_packs
```

## Output Format

Generated Decision Packs are saved as JSON files with the following structure:

```json
{
  "title": "Growth Experiment Title",
  "hypothesis": "Clear hypothesis statement",
  "expected_lift": {
    "level": "medium",
    "metric": "conversion rate"
  },
  "confidence": "Medium",
  "confidence_justification": [
    "Reason 1",
    "Reason 2"
  ],
  "risks": [
    "Risk 1",
    "Risk 2"
  ],
  "assets_needed": [
    "LP snippet",
    "3-email sequence",
    "LinkedIn copy"
  ],
  "suggested_execution_steps": [
    "Step 1",
    "Step 2",
    "Step 3"
  ]
}
```

## File Naming Convention

Decision Packs are saved as:
```
{domain}__{timestamp}.json
```

Example: `techcrunch.com__20241201T143022Z.json`

## Integration with Signal Miner

### Automatic Workflow
1. Run signal miner: `python ../signal_miner.py`
2. Generate Decision Pack: `python generate_pack.py`
3. Review in Streamlit UI: `cd ../ui_app && streamlit run app.py`

### Manual Workflow
```bash
# Step 1: Mine signals
python ../signal_miner.py

# Step 2: Generate Decision Pack
python generate_pack.py --input ../output/signals.json

# Step 3: Check output
ls -la ../output/decision_packs/
```

## Environment Variables

### Required
```bash
OPENAI_API_KEY=your_openai_api_key
```

### Optional (for Pinecone)
```bash
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENV=your_environment
PINECONE_INDEX_NAME=astra-signals-dev  # default
```

## Troubleshooting

### Common Issues

#### 1. OpenAI API Key Missing
```bash
# Error: OPENAI_API_KEY env var is required
# Solution: Set the environment variable
export OPENAI_API_KEY="your_key"
```

#### 2. No Signals Found
```bash
# Error: Input not found
# Solution: Run signal miner first
python ../signal_miner.py
```

#### 3. Pinecone Index Not Found
```bash
# Error: Index 'astra-signals-dev' not found
# Solution: Create the index
python -c "
import pinecone
pinecone.init(api_key='$PINECONE_API_KEY', environment='$PINECONE_ENV')
pinecone.create_index('astra-signals-dev', dimension=1536, metric='cosine')
"
```

#### 4. FAISS Installation Issues
```bash
# Error: No module named 'faiss'
# Solution: Install FAISS
pip install faiss-cpu

# For Windows
pip install faiss-cpu==1.7.4
```

### Testing Your Setup

#### Test OpenAI Connection
```bash
python -c "
import os
from openai import OpenAI
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
response = client.embeddings.create(model='text-embedding-3-small', input=['test'])
print('✅ OpenAI connection working!')
"
```

#### Test Pinecone Connection
```bash
python -c "
import os
import pinecone
pinecone.init(api_key=os.environ['PINECONE_API_KEY'], environment=os.environ['PINECONE_ENV'])
index = pinecone.Index('astra-signals-dev')
print('✅ Pinecone connection working!')
"
```

#### Test FAISS Fallback
```bash
# Unset Pinecone variables
unset PINECONE_API_KEY
unset PINECONE_ENV

# Test
python -c "
from pinecone_helper import get_store
store = get_store(embed_dim=1536)
print('✅ FAISS fallback working!')
"
```

## Performance Considerations

### Embedding Models
- **text-embedding-3-small**: Fast, good quality, 1536 dimensions
- **text-embedding-3-large**: Slower, better quality, 3072 dimensions
- **text-embedding-ada-002**: Legacy, 1536 dimensions

### LLM Models
- **gpt-4o-mini**: Fast, cost-effective, good quality
- **gpt-4o**: Better quality, more expensive
- **gpt-4**: Best quality, most expensive

### Storage Performance
- **Pinecone**: Good for production, persistent storage
- **FAISS**: Very fast for local development, in-memory only

## Advanced Usage

### Custom Prompt Template
```bash
# Edit the prompt template
vim prompts/decision_pack_template.txt

# Regenerate packs
python generate_pack.py
```

### Batch Processing
```bash
# Process multiple signal files
for file in ../output/*.json; do
  python generate_pack.py --input "$file"
done
```

### Integration with CI/CD
```bash
# Example GitHub Actions step
- name: Generate Decision Packs
  run: |
    cd Signal_Miner
    export OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}
    python rfg/generate_pack.py
```

## API Usage

### Programmatic Usage
```python
from generate_pack import generate_pack_for_run

# Generate pack for specific run
result = generate_pack_for_run(
    run_path="path/to/signals.json",
    model="gpt-4o-mini",
    embed_model="text-embedding-3-small"
)

pack = result["pack"]
metadata = result["metadata"]
```

### Custom Vector Store
```python
from pinecone_helper import get_store, VectorStore

# Use custom store
class CustomStore(VectorStore):
    def upsert(self, vectors):
        # Custom implementation
        pass
    
    def query(self, vector, top_k=8):
        # Custom implementation
        pass

# Use in generator
store = CustomStore()
```

## Monitoring and Logging

### Enable Debug Logging
```bash
export PYTHONPATH=.
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from generate_pack import generate_pack_for_run
# ... your code
"
```

### Performance Metrics
The generator logs:
- Embedding time (milliseconds)
- Retrieval latency (milliseconds)
- Citation scores
- Model usage

## Next Steps

1. **Set up Pinecone** (see [setup_pinecone.md](setup_pinecone.md))
2. **Test the workflow** with sample data
3. **Integrate with Streamlit UI** for human review
4. **Deploy to production** with proper monitoring

For more information, see:
- [setup_pinecone.md](setup_pinecone.md) - Pinecone setup guide
- [../README.md](../README.md) - Main project documentation
- [../ui_app/README.md](../ui_app/README.md) - Streamlit UI guide
