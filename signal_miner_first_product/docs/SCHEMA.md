# GrowthSignal MVP - Data Schema & Provenance

## Overview

This document describes the JSON data structures, field types, and provenance tracking used throughout the GrowthSignal platform. All schemas include field descriptions, data types, and examples.

## Signal Mining Outputs

### signals.json (Combined Results)

**File Location**: `Signal_Miner/output/signals.json`

**Structure**: Array of per-site mining results

```json
[
  {
    "url": "https://example.com",
    "domain": "example.com",
    "timestamp": "2024-01-15T14:30:22.123456Z",
    "error": null,
    "snapshot": "snapshots/example.com_20240115T143022Z.html",
    "signals": {
      "headlines_paragraphs": [
        "Example Company Launches New SaaS Platform",
        "Our platform helps businesses scale faster with AI-powered insights",
        "Pricing starts at $99/month for small teams"
      ],
      "lists": [
        ["Feature 1", "Feature 2", "Feature 3"],
        ["Benefit A", "Benefit B", "Benefit C"]
      ],
      "prices": ["$99", "$199", "$299"]
    }
  }
]
```

**Field Descriptions**:
- `url`: Original URL that was mined
- `domain`: Extracted domain name (www. stripped)
- `timestamp`: ISO 8601 timestamp in UTC
- `error`: Error message if mining failed, null if successful
- `snapshot`: Path to HTML snapshot file (relative to output directory)
- `signals`: Extracted structured data

**Signals Structure**:
- `headlines_paragraphs`: Array of text snippets (min 4 words)
- `lists`: Array of list item arrays
- `prices`: Array of detected price strings ($X.XX format)

### Per-Site Results

**File Location**: `Signal_Miner/output/signals/domain_timestamp.json`

**Structure**: Individual site mining result (same as array items above)

**Naming Convention**: `{domain}_{YYYYMMDDTHHMMSSZ}.json`

### HTML Snapshots

**File Location**: `Signal_Miner/output/snapshots/domain_timestamp.html`

**Content**: Raw HTML content from mining operation

**Purpose**: Audit trail, compliance verification, debugging

**Naming Convention**: `{domain}_{YYYYMMDDTHHMMSSZ}.html`

## Decision Pack Schema

### Generated Decision Pack

**File Location**: `Signal_Miner/output/decision_packs/domain_timestamp.json`

**Structure**: Complete Decision Pack with generation metadata

```json
{
  "title": "Launch Enterprise Pricing Tier Based on Competitor Analysis",
  "hypothesis": "Adding an enterprise pricing tier at $499/month could increase ARR by 25-40% by capturing larger customers currently underserved by our basic plans.",
  "expected_lift": {
    "level": "high",
    "metric": "monthly_recurring_revenue",
    "range": "25-40%",
    "timeframe": "3-6 months"
  },
  "confidence": 0.85,
  "confidence_justification": [
    "Competitor pricing analysis shows clear enterprise tier gap",
    "Customer feedback indicates demand for advanced features",
    "Market research supports premium pricing for enterprise features"
  ],
  "risks": [
    "Potential cannibalization of existing premium plans",
    "Enterprise sales cycle longer than SMB",
    "Support infrastructure may need scaling"
  ],
  "assets_needed": [
    "Enterprise landing page with feature comparison",
    "Sales deck highlighting ROI and enterprise benefits",
    "Customer case studies and testimonials"
  ],
  "suggested_execution_steps": [
    "Week 1: Design enterprise pricing page and sales materials",
    "Week 2: Create A/B test with existing premium customers",
    "Week 3: Launch soft launch to beta enterprise customers",
    "Week 4: Monitor metrics and gather feedback"
  ],
  "metadata": {
    "generation_model": "gpt-4o-mini",
    "embedding_model": "text-embedding-3-small",
    "embedding_time": "2024-01-15T14:30:22.123456Z",
    "vector_store": "faiss",
    "top_citations": [
      {
        "snippet": "Enterprise customers need advanced analytics and team collaboration features",
        "source": "competitor.com/pricing",
        "relevance_score": 0.92
      },
      {
        "snippet": "Pricing tiers range from $99 to $499 with enterprise custom pricing",
        "source": "competitor.com/enterprise",
        "relevance_score": 0.89
      }
    ],
    "generation_time_seconds": 8.45,
    "snippets_processed": 46,
    "vector_search_time_ms": 125
  }
}
```

**Required Fields**:
- `title`: String - Descriptive experiment title
- `hypothesis`: String - Clear hypothesis statement
- `expected_lift`: Object - Lift predictions and metrics
- `confidence`: Number (0.0-1.0) - Confidence level
- `confidence_justification`: Array of strings - Supporting evidence
- `risks`: Array of strings - Potential risks and mitigation
- `assets_needed`: Array of strings - Required marketing assets
- `suggested_execution_steps`: Array of strings - Implementation timeline

**Optional Fields**:
- `metadata`: Object - Generation provenance and technical details

### Expected Lift Structure

```json
{
  "level": "low|medium|high",
  "metric": "conversion_rate|revenue|user_engagement|etc",
  "range": "10-15%|25-40%|etc",
  "timeframe": "1-2 weeks|3-6 months|etc"
}
```

**Level Values**:
- `low`: 5-15% improvement
- `medium`: 15-30% improvement  
- `high`: 30%+ improvement

**Common Metrics**:
- `conversion_rate`: Signup/purchase conversion
- `monthly_recurring_revenue`: MRR increase
- `user_engagement`: Time on site, feature usage
- `customer_acquisition_cost`: CAC reduction
- `retention_rate`: Customer retention improvement

### Metadata Structure

**Generation Information**:
- `generation_model`: LLM used (e.g., "gpt-4o-mini")
- `embedding_model`: Embedding model (e.g., "text-embedding-3-small")
- `embedding_time`: ISO timestamp of embedding generation
- `vector_store`: Storage backend ("pinecone" or "faiss")

**Performance Metrics**:
- `generation_time_seconds`: Total LLM generation time
- `snippets_processed`: Number of text snippets analyzed
- `vector_search_time_ms`: Vector similarity search time

**Citation Tracking**:
- `top_citations`: Array of most relevant source snippets
- `snippet`: Text content from source
- `source`: URL or identifier of source
- `relevance_score`: Similarity score (0.0-1.0)

## PR Preview Schema

### PR Preview File

**File Location**: `Signal_Miner/output/previews/domain_pr_preview.json`

**Structure**: GitHub PR preview when live creation unavailable

```json
{
  "branch_name": "play/launch-enterprise-pricing-tier-20240115T143022Z",
  "title": "Launch Enterprise Pricing Tier Based on Competitor Analysis",
  "files": {
    "decision_pack": "decision_packs/example.com_20240115T143022Z.json",
    "landing_page": "landing_pages/example.com_20240115T143022Z.html"
  },
  "commit_message": "Add growth experiment: Launch Enterprise Pricing Tier\n\nHypothesis: Adding an enterprise pricing tier at $499/month could increase ARR by 25-40%...\nExpected: high lift on monthly_recurring_revenue",
  "domain": "example.com",
  "slug": "launch-enterprise-pricing-tier",
  "stamp": "20240115T143022Z",
  "diff_text": "diff --git a/decision_packs/example.com_20240115T143022Z.json b/decision_packs/example.com_20240115T143022Z.json\nnew file mode 100644\nindex 0000000..a1b2c3d\n--- /dev/null\n+++ b/decision_packs/example.com_20240115T143022Z.json\n@@ -0,0 +1,45 @@\n+{\n+  \"title\": \"Launch Enterprise Pricing Tier...\",\n+  \"hypothesis\": \"Adding an enterprise pricing tier...\",\n+  ...\n+}\n\ndiff --git a/landing_pages/example.com_20240115T143022Z.html b/landing_pages/example.com_20240115T143022Z.html\nnew file mode 100644\nindex 0000000..d4e5f6g\n--- /dev/null\n+++ b/landing_pages/example.com_20240115T143022Z.html\n@@ -0,0 +1,25 @@\n+<!DOCTYPE html>\n+<html>\n+<head>\n+  <title>Enterprise Pricing - Example Company</title>\n+</head>\n+<body>\n+  <h1>Enterprise Pricing</h1>\n+  <p>Advanced features for growing teams...</p>\n+  ...\n+</body>\n+</html>",
  "github_status": "preview_only",
  "created_at": "2024-01-15T14:30:22.123456Z"
}
```

**Field Descriptions**:
- `branch_name`: Git branch name with timestamp suffix
- `title`: PR title from Decision Pack
- `files`: Object mapping file types to paths
- `commit_message`: Descriptive commit message
- `domain`: Source domain for the experiment
- `slug`: URL-safe version of experiment title
- `stamp`: Timestamp suffix for uniqueness
- `diff_text`: Git diff showing file changes
- `github_status`: "preview_only" or "pr_created"
- `created_at`: ISO timestamp of preview generation

**File Paths**:
- `decision_pack`: Path to Decision Pack JSON file
- `landing_page`: Path to generated landing page HTML

## Telemetry Schema

### Telemetry Events

**File Location**: `Signal_Miner/output/telemetry.json`

**Structure**: Array of user action events

```json
[
  {
    "run_id": "example.com__2024-01-15T14:30:22.123456Z",
    "user_email": "user@example.com",
    "action": "generate_pack",
    "timestamp": "2024-01-15T14:30:22.123456Z"
  },
  {
    "run_id": "example.com__2024-01-15T14:30:22.123456Z",
    "user_email": "user@example.com",
    "action": "approve",
    "timestamp": "2024-01-15T14:31:15.654321Z"
  },
  {
    "run_id": "example.com__2024-01-15T14:30:22.123456Z",
    "user_email": "user@example.com",
    "action": "create_pr",
    "timestamp": "2024-01-15T14:31:45.987654Z"
  }
]
```

**Event Types**:
- `generate_pack`: Decision Pack auto-generation
- `approve`: User approval of Decision Pack
- `create_pr`: PR creation or preview generation
- `save_pack`: Manual Decision Pack save
- `view_run`: User viewing mining run details

**Field Descriptions**:
- `run_id`: Unique identifier for mining run
- `user_email`: User email (if provided)
- `action`: Type of user action
- `timestamp`: ISO timestamp of action

## Configuration Files

### URL Configuration

**File Location**: `Signal_Miner/url.txt`

**Format**: One URL per line

```text
https://news.ycombinator.com
https://techcrunch.com
https://example.com
```

### Streamlit Configuration

**File Location**: `ui_app/.streamlit/config.toml`

**Structure**: Streamlit app configuration

```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8f9fa"
textColor = "#1f2937"
font = "sans serif"

[server]
port = 8501
enableCORS = false
enableXsrfProtection = true
```

### Streamlit Secrets

**File Location**: `ui_app/.streamlit/secrets.toml`

**Structure**: Sensitive configuration (not committed)

```toml
demo_password = "your-demo-password-here"
openai_api_key = "sk-your-openai-key"
pinecone_api_key = "your-pinecone-key"
pinecone_env = "your-pinecone-environment"
github_token = "your-github-token"
github_repo = "owner/repo"
```

## Data Provenance Tracking

### Complete Provenance Chain

1. **Source URLs** → `url.txt`
2. **HTML Content** → `snapshots/domain_timestamp.html`
3. **Extracted Signals** → `signals.json` + `signals/domain_timestamp.json`
4. **Vector Embeddings** → OpenAI API + Pinecone/FAISS
5. **Decision Pack** → LLM generation with citations
6. **User Actions** → `telemetry.json`
7. **PR Preview** → `previews/domain_pr_preview.json`

### Provenance Fields

**In Decision Packs**:
- `metadata.generation_model`: LLM used
- `metadata.embedding_model`: Embedding model
- `metadata.vector_store`: Storage backend
- `metadata.top_citations`: Source snippets with scores

**In PR Previews**:
- `files.decision_pack`: Path to source Decision Pack
- `files.landing_page`: Path to generated landing page
- `diff_text`: Exact file changes

**In Telemetry**:
- `run_id`: Links to specific mining run
- `action`: User action performed
- `timestamp`: When action occurred

## Data Validation

### Required Field Validation

**Decision Pack Required Fields**:
```python
REQUIRED_FIELDS = [
    "title", "hypothesis", "expected_lift", "confidence",
    "confidence_justification", "risks", "assets_needed",
    "suggested_execution_steps"
]
```

**Expected Lift Required Fields**:
```python
LIFT_REQUIRED_FIELDS = ["level", "metric", "range", "timeframe"]
```

**Metadata Required Fields**:
```python
METADATA_REQUIRED_FIELDS = [
    "generation_model", "embedding_model", "embedding_time",
    "vector_store", "top_citations"
]
```

### Data Type Validation

**String Fields**: Must be non-empty strings
**Number Fields**: Must be valid numbers (confidence: 0.0-1.0)
**Array Fields**: Must be non-empty arrays
**Object Fields**: Must have required nested fields
**Timestamp Fields**: Must be valid ISO 8601 format

### Content Validation

**Title**: 10-200 characters, descriptive
**Hypothesis**: 50-500 characters, clear statement
**Confidence**: 0.0-1.0 range
**Citations**: At least 2, maximum 10
**Execution Steps**: At least 3, maximum 10

## File Naming Conventions

### Timestamp Format

**Format**: `YYYYMMDDTHHMMSSZ`

**Examples**:
- `20240115T143022Z` = January 15, 2024, 14:30:22 UTC
- `20241231T235959Z` = December 31, 2024, 23:59:59 UTC

**Components**:
- `YYYY`: 4-digit year
- `MM`: 2-digit month (01-12)
- `DD`: 2-digit day (01-31)
- `T`: Literal 'T' separator
- `HH`: 2-digit hour (00-23)
- `MM`: 2-digit minute (00-59)
- `SS`: 2-digit second (00-59)
- `Z`: UTC timezone indicator

### File Naming Patterns

**Signals**: `{domain}_{timestamp}.json`
**Snapshots**: `{domain}_{timestamp}.html`
**Decision Packs**: `{domain}_{timestamp}.json`
**PR Previews**: `{domain}_pr_preview.json`

**Examples**:
- `news.ycombinator.com_20240115T143022Z.json`
- `techcrunch.com_20240115T143022Z.html`
- `example.com_20240115T143022Z.json`
- `example.com_pr_preview.json`

## Data Retention & Cleanup

### Retention Policies

**HTML Snapshots**: 30 days (active monitoring)
**Decision Packs**: 90 days (pilot completion)
**PR Previews**: 180 days (compliance review)
**Telemetry**: 365 days (audit purposes)

### Cleanup Process

**Automatic Cleanup** (planned):
```bash
# Daily cleanup script
find output/snapshots -name "*.html" -mtime +30 -delete
find output/decision_packs -name "*.json" -mtime +90 -delete
find output/previews -name "*.json" -mtime +180 -delete
```

**Manual Cleanup**:
```powershell
# PowerShell cleanup commands
Get-ChildItem "Signal_Miner/output/snapshots" | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item
Get-ChildItem "Signal_Miner/output/decision_packs" | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-90)} | Remove-Item
Get-ChildItem "Signal_Miner/output/previews" | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-180)} | Remove-Item
```

## Schema Evolution

### Versioning Strategy

**Current Version**: 1.0.0

**Backward Compatibility**: New fields are optional, existing fields unchanged

**Migration Path**: Gradual field deprecation with warnings

### Planned Schema Changes

**Version 1.1.0**:
- Add `experiment_type` field to Decision Packs
- Add `target_audience` field for segmentation
- Add `success_metrics` array for KPIs

**Version 1.2.0**:
- Add `a_b_test_config` for experiment setup
- Add `rollback_plan` for risk mitigation
- Add `stakeholder_approval` workflow

### Schema Validation

**Current**: Basic field presence and type checking
**Planned**: JSON Schema validation with detailed error messages
**Future**: OpenAPI specification for API endpoints

