# GrowthSignal (Astra Sage Pilot Productized Service)

Turn public competitor signals into actionable Decision Packs (hypothesis, expected lift, risks) and ready-to-ship assets (LP snippet, email sequence, PR draft) — with a human-in-the-loop approval and safe execution.

## Quick Start

### 1. Install Dependencies
```bash
cd Signal_Miner
pip install -r requirements.txt
```

### 2. Run Signal Miner
```bash
python signal_miner.py
```

### 3. Generate Decision Pack (RAG)
```bash
# Set OpenAI API key
export OPENAI_API_KEY="your_key"

# Generate pack from latest signals
python rfg/generate_pack.py

# Or specify input file
python rfg/generate_pack.py --input output/signals.json --model gpt-4o-mini
```

**📖 For detailed setup instructions, see:**
- [RAG Module Guide](Signal_Miner/rfg/README.md) - Complete usage guide
- [Pinecone Setup](Signal_Miner/rfg/setup_pinecone.md) - Vector database setup

**📋 For pilot program delivery, see:**
- [Pilot Workflow](WORKFLOW.md) - Step-by-step delivery checklist
- [Compliance Policy](COMPLIANCE.md) - Privacy, robots.txt, and data retention policies

### 4. Launch Streamlit UI
```bash
cd ../ui_app
pip install -r requirements.txt
streamlit run app.py
```

## Testing

### Run All Tests
```bash
cd Signal_Miner
python run_tests.py
```

### Test RAG Setup
```bash
cd Signal_Miner/rfg
python test_setup.py
```

### Individual Test Commands
```bash
# Unit tests with coverage
pytest rfg/tests/ executor/tests/ -v --cov=rfg --cov=executor --cov-report=term-missing

# Linting
flake8 rfg/ executor/ --count --select=E9,F63,F7,F82 --show-source --statistics

# Security checks
bandit -r rfg/ executor/ -f txt
```

### CI/CD
- **GitHub Actions**: Automated testing on push to `main`, `develop`, and `feature/*` branches
- **Coverage**: Minimum 80% test coverage required
- **Security**: Bandit security scanning
- **Linting**: Flake8 code quality checks

## Architecture

### Core Modules
- **`signal_miner.py`**: Web scraping and signal extraction
- **`rfg/`**: RAG-based Decision Pack generation
- **`executor/`**: GitHub PR creation and execution
- **`ui_app/`**: Streamlit web interface

### Data Flow
1. **Mining**: Extract signals from competitor URLs
2. **RAG**: Generate Decision Packs using OpenAI embeddings + retrieval
3. **UI**: Human review and editing
4. **Execution**: Create GitHub PRs with assets

## Environment Variables

```bash
# Required for RAG
export OPENAI_API_KEY="your_openai_key"

# Optional for Pinecone (falls back to local FAISS)
export PINECONE_API_KEY="your_pinecone_key"
export PINECONE_ENV="your_pinecone_env"

# Optional for GitHub PR creation
export GITHUB_TOKEN="your_github_token"
export GITHUB_REPO="owner/repo"
```

## Features

### Signal Mining
- Multi-site scraping with error handling
- Structured data extraction (headlines, lists, prices)
- HTML snapshots for audit trail
- Configurable allowlist URLs

### RAG Decision Pack Generation
- OpenAI embeddings (text-embedding-3-small)
- Pinecone/FAISS vector storage
- GPT-4o-mini for pack generation
- Citation tracking and provenance

### Streamlit UI
- Dashboard with run metrics
- Auto-generate Decision Packs
- Interactive editing and review
- GitHub PR creation workflow

### GitHub Integration
- Automated branch creation (`play/<slug>-<timestamp>`)
- Decision Pack and landing page commits
- PR template with experiment details
- Preview mode when no token available

## Development

### Project Structure
```
signal_miner_first_product/
├── Signal_Miner/
│   ├── signal_miner.py          # Core mining logic
│   ├── rfg/                     # RAG module
│   │   ├── generate_pack.py     # Decision Pack generation
│   │   ├── pinecone_helper.py   # Vector store abstraction
│   │   └── tests/               # Unit tests
│   ├── executor/                # PR execution
│   │   ├── pr_executor.py       # GitHub PR creation
│   │   └── tests/               # Unit tests
│   └── output/                  # Generated artifacts
├── ui_app/                      # Streamlit interface
└── .github/workflows/           # CI/CD configuration
```

### Testing Strategy
- **Unit Tests**: Mocked OpenAI and GitHub APIs
- **Integration Tests**: End-to-end workflows
- **Coverage**: 80% minimum requirement
- **Security**: Bandit vulnerability scanning
- **Quality**: Flake8 linting and style checks

## Acceptance Criteria

### MVP Features ✅
- [x] Signal mining from allowlist URLs
- [x] RAG-based Decision Pack generation
- [x] Streamlit UI with auto-generation
- [x] GitHub PR creation workflow
- [x] Comprehensive test suite
- [x] CI/CD pipeline

### Metrics Targets
- **Decision Pack Accuracy**: >80% reasonable fields on manual review
- **Test Coverage**: >80% code coverage
- **CI Pass Rate**: 100% on main branch
- **Security**: Zero high-severity vulnerabilities

## Pilot Program & Compliance

### Pilot Program Delivery
GrowthSignal offers a $149 pilot program for qualified growth teams. The pilot includes:
- 3 months of full platform access
- Dedicated onboarding and support
- Compliance monitoring and reporting
- Success metrics tracking and ROI analysis

**📋 See [WORKFLOW.md](WORKFLOW.md) for complete pilot delivery checklist**

### Compliance & Privacy
GrowthSignal operates under strict compliance policies:
- **Robots.txt Respect**: Strict adherence to website crawling policies
- **PII Protection**: Automatic detection and redaction of personal data
- **Data Retention**: 30-day snapshot retention with automatic cleanup
- **Pilot Allowlist**: Pre-approved competitor domains only

**📋 See [COMPLIANCE.md](COMPLIANCE.md) for complete compliance policy**

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`python run_tests.py`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
