# GrowthSignal MVP - Windows/PowerShell Runbook

## Overview

This runbook provides step-by-step instructions for running the GrowthSignal MVP on Windows with Python 3.13. All commands are optimized for PowerShell and assume you're working from the `signal_miner_first_product` directory.

## Prerequisites

### Python Environment
- **Python Version**: 3.13.7 (tested)
- **Package Manager**: pip (included with Python)
- **Shell**: PowerShell (Windows Terminal recommended)

### Required Accounts
- **OpenAI**: API key for embeddings and LLM generation
- **Pinecone** (optional): For production vector storage
- **GitHub** (optional): For live PR creation

## Installation & Setup

### 1. Install Dependencies

```powershell
# Install Signal_Miner dependencies
py -m pip install -r Signal_Miner/requirements.txt

# Install UI dependencies
py -m pip install -r ui_app/requirements.txt
```

**Expected Output**: Successfully installed packages with version numbers

**Troubleshooting**:
- If `py` command not found, use `python` instead
- If permission errors, run PowerShell as Administrator
- For FAISS issues on Windows, ensure you have Visual C++ build tools

### 2. Set Environment Variables

```powershell
# Set OpenAI API key (required)
$env:OPENAI_API_KEY="sk-your-openai-api-key-here"

# Set Pinecone credentials (optional - falls back to FAISS)
$env:PINECONE_API_KEY="your-pinecone-api-key"
$env:PINECONE_ENV="your-pinecone-environment"

# Set GitHub credentials (optional - falls back to preview mode)
$env:GITHUB_TOKEN="your-github-personal-access-token"
$env:GITHUB_REPO="owner/repo-name"

# Verify environment variables
Get-ChildItem Env: | Where-Object {$_.Name -like "*OPENAI*" -or $_.Name -like "*PINECONE*" -or $_.Name -like "*GITHUB*"}
```

**Persistent Environment Variables** (optional):
```powershell
# Set persistent environment variables (survives PowerShell restarts)
setx OPENAI_API_KEY "sk-your-openai-api-key-here"
setx PINECONE_API_KEY "your-pinecone-api-key"
setx PINECONE_ENV "your-pinecone-environment"
setx GITHUB_TOKEN "your-github-personal-access-token"
setx GITHUB_REPO "owner/repo-name"

# Note: You'll need to restart PowerShell for persistent vars to take effect
```

## Core Workflows

### 3. Run Signal Mining

```powershell
# Basic mining with default settings
py Signal_Miner/signal_miner.py

# Mining with custom parameters
py Signal_Miner/signal_miner.py Signal_Miner/url.txt --limit 6 --out Signal_Miner/output/signals.json

# Mining with verbose output
py Signal_Miner/signal_miner.py --verbose --limit 10
```

**Parameters**:
- `--limit N`: Maximum number of URLs to process
- `--out PATH`: Output file path
- `--verbose`: Detailed logging
- `--help`: Show all options

**Expected Output**:
```
Processing 6 URLs...
✅ news.ycombinator.com: 15 signals extracted
✅ techcrunch.com: 23 signals extracted
✅ example.com: 8 signals extracted
Total: 46 signals across 3 domains
Results saved to: Signal_Miner/output/signals.json
```

**Troubleshooting**:
- **Permission errors**: Run PowerShell as Administrator
- **URL errors**: Check `Signal_Miner/url.txt` format (one URL per line)
- **Memory issues**: Reduce `--limit` for large sites

### 4. Generate Decision Pack (RAG)

```powershell
# Generate from latest signals
py Signal_Miner/rfg/generate_pack.py

# Generate from specific file
py Signal_Miner/rfg/generate_pack.py --input Signal_Miner/output/signals.json --model gpt-4o-mini

# Generate with custom output directory
py Signal_Miner/rfg/generate_pack.py --outdir Signal_Miner/output/decision_packs
```

**Parameters**:
- `--input PATH`: Input signals file
- `--model MODEL`: LLM model (default: gpt-4o-mini)
- `--outdir PATH`: Output directory for Decision Packs

**Expected Output**:
```
🔍 Loading signals from: Signal_Miner/output/signals.json
📊 Found 46 signals across 3 domains
🧠 Generating embeddings with OpenAI...
🔍 Performing vector similarity search...
🤖 Generating Decision Pack with GPT-4o-mini...
✅ Decision Pack generated successfully
📁 Saved to: Signal_Miner/output/decision_packs/example.com_20240115T143022Z.json
```

**Troubleshooting**:
- **OpenAI API errors**: Verify `OPENAI_API_KEY` environment variable
- **FAISS fallback**: If Pinecone unavailable, will use local FAISS
- **Memory issues**: Reduce number of signals with `--limit` in mining

### 5. Launch Streamlit UI

```powershell
# Navigate to UI directory
cd ui_app

# Launch Streamlit app
streamlit run app.py

# Launch with custom port
streamlit run app.py --server.port 8501

# Launch with custom address (for network access)
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

**Expected Output**:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.1.100:8501

For more detailed logs, run 'streamlit run app.py --logger.level=debug'
```

**Browser Access**: Open http://localhost:8501 in your browser

**Troubleshooting**:
- **Port conflicts**: Use `--server.port 8502` for different port
- **Firewall issues**: Allow Streamlit through Windows Firewall
- **Browser issues**: Try incognito/private browsing mode

## UI Workflows

### 6. Dashboard Navigation

**Access Points**:
- **Dashboard**: Overview of mining runs and metrics
- **Run Detail**: View specific mining results and Decision Packs
- **Settings**: Configure URLs and API keys

**Key Actions**:
- View last run time and signal counts
- Navigate to specific mining runs
- Access Decision Pack generation

### 7. Decision Pack Generation

**Workflow**:
1. **Navigate to Run Detail** page for a specific mining run
2. **Click "🚀 Auto-generate Decision Pack"** button
3. **Wait for generation** (5-15 seconds)
4. **Review generated content** in Decision Pack editor
5. **Edit fields** as needed
6. **Click "💾 Save Decision Pack"** to save

**Expected Results**:
- All Decision Pack fields populated
- Generation metadata displayed (model, timing, citations)
- File saved to `Signal_Miner/output/decision_packs/`

**Troubleshooting**:
- **Generation fails**: Check OpenAI API key and internet connection
- **Fields missing**: Verify signals.json has sufficient content
- **Save errors**: Check write permissions to output directory

### 8. Approval & PR Creation

**Workflow**:
1. **Fill in GitHub credentials** (token and repo)
2. **Click "🚀 Approve & Create PR"** button
3. **Confirm action** in modal dialog
4. **Wait for processing** (PR creation or preview generation)

**Expected Results**:
- **With GitHub token**: Creates live PR on GitHub
- **Without token**: Generates preview file in `Signal_Miner/output/previews/`

**Output Files**:
```
Signal_Miner/output/previews/
└── domain_pr_preview.json
    ├── branch_name: "play/experiment-name-timestamp"
    ├── files: Decision Pack and landing page paths
    ├── commit_message: Descriptive commit message
    └── diff_text: Preview of changes
```

## Output Locations

### Signal Mining Results
```
Signal_Miner/output/
├── signals.json              # Combined results from all URLs
├── signals/                  # Individual site results
│   ├── domain1_timestamp.json
│   └── domain2_timestamp.json
└── snapshots/                # HTML snapshots for audit
    ├── domain1_timestamp.html
    └── domain2_timestamp.html
```

### Decision Packs
```
Signal_Miner/output/decision_packs/
└── domain_timestamp.json     # Generated Decision Pack with metadata
```

### PR Previews
```
Signal_Miner/output/previews/
└── domain_pr_preview.json    # PR preview when GitHub token unavailable
```

### Telemetry
```
Signal_Miner/output/telemetry.json  # User action tracking
```

## Testing & Validation

### 9. Run Test Suite

```powershell
# Navigate to Signal_Miner directory
cd Signal_Miner

# Run all tests
py run_tests.py

# Run specific test modules
py -m pytest rfg/tests/ -v
py -m pytest executor/tests/ -v

# Run with coverage
py -m pytest --cov=rfg --cov=executor --cov-report=html
```

**Expected Output**:
```
============================= test session starts =============================
collecting ... collected 15 tests
test_generate_pack.py::test_load_signals PASSED
test_generate_pack.py::test_collect_snippets PASSED
...
============================= 15 passed in 12.34s ============================
```

### 10. Test RAG Setup

```powershell
# Test OpenAI connectivity
py Signal_Miner/rfg/test_setup.py

# Test specific components
py -c "from Signal_Miner.rfg.pinecone_helper import get_store; print('FAISS fallback working')"
```

## Troubleshooting

### Common Issues

**Python Path Issues**:
```powershell
# Verify Python installation
py --version
py -c "import sys; print(sys.executable)"

# Check PATH environment
$env:PATH -split ';' | Where-Object {$_ -like "*Python*"}
```

**Permission Errors**:
```powershell
# Run PowerShell as Administrator
# Or check folder permissions
Get-Acl "Signal_Miner/output" | Format-List

# Create output directories if missing
New-Item -ItemType Directory -Path "Signal_Miner/output" -Force
New-Item -ItemType Directory -Path "Signal_Miner/output/decision_packs" -Force
New-Item -ItemType Directory -Path "Signal_Miner/output/previews" -Force
```

**API Key Issues**:
```powershell
# Verify environment variables
Get-ChildItem Env: | Where-Object {$_.Name -like "*OPENAI*"}

# Test OpenAI connectivity
py -c "import os; print('OpenAI Key:', os.environ.get('OPENAI_API_KEY', 'NOT SET')[:20] + '...')"
```

**Memory Issues**:
```powershell
# Check available memory
Get-ComputerInfo | Select-Object TotalPhysicalMemory, AvailablePhysicalMemory

# Reduce processing limits
py Signal_Miner/signal_miner.py --limit 3
```

### Performance Optimization

**For Large Datasets**:
```powershell
# Process in smaller batches
py Signal_Miner/signal_miner.py --limit 5

# Use FAISS instead of Pinecone for local processing
# (Automatic fallback when PINECONE_API_KEY not set)
```

**For Faster UI**:
```powershell
# Launch Streamlit with optimizations
streamlit run app.py --server.headless true --server.enableCORS false
```

## Monitoring & Logs

### Application Logs
- **Signal Mining**: Console output with progress and errors
- **RAG Generation**: Detailed timing and API call logs
- **UI Operations**: Streamlit logs in terminal

### Error Tracking
```powershell
# Check for error logs
Get-ChildItem "Signal_Miner/output" -Recurse -Filter "*.log" | Select-Object Name, Length

# Monitor telemetry
Get-Content "Signal_Miner/output/telemetry.json" | ConvertFrom-Json | Format-Table
```

### Health Checks
```powershell
# Verify output directories exist
Test-Path "Signal_Miner/output/decision_packs"
Test-Path "Signal_Miner/output/previews"

# Check file permissions
Get-Acl "Signal_Miner/output" | Format-List
```

## Security Notes

### API Key Management
- **Never commit API keys** to version control
- **Use environment variables** for sensitive data
- **Rotate keys regularly** for production use

### Data Privacy
- **HTML snapshots** contain raw website content
- **PII detection** automatically redacts personal data
- **Data retention** policy: 30 days for active monitoring

### Compliance
- **Robots.txt respect** implemented but not enforced
- **Rate limiting** configurable but not automatic
- **User-agent** identifies GrowthSignal for transparency

## Next Steps

### Immediate Actions
1. **Test end-to-end workflow** with sample URLs
2. **Validate Decision Pack generation** quality
3. **Test PR preview creation** without GitHub token

### Production Readiness
1. **Implement robots.txt enforcement**
2. **Add rate limiting** and crawl delays
3. **Set up monitoring** and alerting
4. **Configure backup** and retention policies

### Scaling Considerations
1. **Async processing** for multiple URLs
2. **Database storage** for metadata
3. **Cloud storage** for HTML snapshots
4. **API layer** for external integrations

## Support & Resources

### Documentation
- **Architecture**: `docs/ARCHITECTURE.md`
- **Compliance**: `COMPLIANCE.md`
- **Pilot Workflow**: `WORKFLOW.md`

### Testing
- **Unit Tests**: `Signal_Miner/rfg/tests/`, `Signal_Miner/executor/tests/`
- **Integration**: End-to-end workflow validation
- **Coverage**: Minimum 80% requirement

### Troubleshooting
- **Common Issues**: See troubleshooting section above
- **Error Messages**: Check console output and logs
- **Performance**: Monitor memory usage and API response times

