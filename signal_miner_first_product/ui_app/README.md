## GrowthSignal UI (Streamlit)

Run the UI:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app reads miner artifacts from `../Signal_Miner/output`.

### Features

- **Dashboard**: View last runs, extracted signals count, and navigate to run details
- **Run Detail**: 
  - View evidence from mined signals
  - Auto-generate Decision Pack using RAG (requires OPENAI_API_KEY)
  - Edit and save Decision Packs
  - Generate assets (LP snippet, email sequence, LinkedIn copy)
  - **Auth-gated Approvals**: Approve & Create PR requires demo password
  - **Create GitHub PRs** with Decision Pack and landing page (with confirmation modal)
- **Settings**: Configure allowlist URLs and API keys

### Environment Variables

Set these environment variables before running:

```bash
# Required for auto-generation
export OPENAI_API_KEY="your_openai_key"

# Optional for Pinecone vector store (falls back to local FAISS)
export PINECONE_API_KEY="your_pinecone_key"
export PINECONE_ENV="your_pinecone_env"

# Optional for GitHub PR creation
export GITHUB_TOKEN="your_github_token"
export GITHUB_REPO="owner/repo"
```

### Demo Authentication (Secrets)

Add a demo password to Streamlit secrets so Approve actions are gated:

```toml
# .streamlit/secrets.toml
demo_password = "your_demo_password"
```

Optionally set a user email at sign-in; it's stored in session and logged in telemetry.

### Auto-Generate Decision Pack

1. Navigate to "Run detail" for any mined site
2. Click "🚀 Auto-generate Decision Pack"
3. The app will:
   - Load the site's signals
   - Create embeddings using OpenAI
   - Store vectors in Pinecone (or local FAISS)
   - Retrieve top 8 relevant snippets
   - Generate a Decision Pack using GPT-4o-mini
   - Auto-fill all form fields
   - Show generation metadata and citations

### Create GitHub PRs

1. Fill in the Decision Pack fields (auto-generate or manual)
2. Add your landing page content in the Assets section
3. Configure GitHub settings:
   - **GitHub Token**: Personal access token with repo permissions
   - **GitHub Repository**: Target repo in format `owner/repo`
4. Sign in with the demo password (top of Run Detail)
5. Click "🚀 Approve & Create PR" and confirm in the modal
5. The app will:
   - Save the Decision Pack to `output/decision_packs/`
   - Generate a landing page HTML file
   - Create a branch `play/<slug>-<timestamp>`
   - Commit both files to the branch
   - Create a PR with formatted description
   - Return the PR URL

**Without GitHub Token**: Creates a preview JSON file in `output/previews/` with branch info and file diffs.

### Telemetry (Pilot Metrics)

The UI records basic usage metrics to `../Signal_Miner/output/telemetry.json`:

- run_id (domain__timestamp)
- user_email (if provided at sign-in)
- action: one of `generate_pack`, `approve`, `create_pr`
- timestamp (UTC)

Telemetry is best-effort and never blocks UI actions.

### Manual Workflow

1. Run the miner: `python ../Signal_Miner/signal_miner.py`
2. Open the UI and navigate to Dashboard
3. Click "View run" on any site
4. Auto-generate or manually edit the Decision Pack
5. Save the pack to `../Signal_Miner/output/decision_packs/`
6. Create GitHub PR or preview

### GitHub Token Setup

1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate a new token with `repo` permissions
3. Copy the token and paste it in the UI
4. The token is stored locally and not committed to the repository


