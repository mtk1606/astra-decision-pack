## Next.js + Tailwind Spec for GrowthSignal UI

This document maps the existing Streamlit MVP to a Next.js + Tailwind implementation with pages, components, and API routes. It includes TypeScript-like prop contracts and JSON Schemas so a frontend dev can implement quickly.

### Tech assumptions
- Next.js 14 (App Router not required; this spec uses Pages Router for simplicity)
- TailwindCSS configured
- TypeScript recommended (prop types below are TS), but pages can be `.jsx` as requested
- Environment variables via `.env.local`

---

## Project structure
```
.
├─ pages/
│  ├─ index.jsx                  # Dashboard
│  ├─ run/
│  │  └─ [id].jsx               # Run detail (id = domain or run_id)
│  └─ api/
│     ├─ runs.js                # GET list, GET one
│     ├─ generate-pack.js       # POST generate
│     └─ create-pr.js           # POST create PR or preview
├─ components/
│  ├─ EvidenceList.tsx
│  ├─ DecisionPackEditor.tsx
│  ├─ AssetPreview.tsx
│  └─ ApproveModal.tsx
├─ lib/
│  ├─ api.ts                    # client helpers (fetch wrappers)
│  └─ schemas.ts                # shared TS types (mirrors JSON Schemas)
├─ styles/
│  └─ globals.css
└─ tailwind.config.js
```

Environment variables:
```
NEXT_DEMO_PASSWORD=...           # Gate Approve actions
BACKEND_BASE_URL=http://localhost:8501  # If proxying to Python backend (optional)
OPENAI_API_KEY=...               # If server calls OpenAI directly
GITHUB_TOKEN=...                 # If server calls GitHub directly
GITHUB_REPO=owner/repo
```

---

## Data models (TypeScript types)
```ts
// lib/schemas.ts
export type Citation = {
  score: number;
  snippet: string;
  source_url?: string;
  snapshot_file?: string;
};

export type DecisionPack = {
  title: string;
  hypothesis: string;
  expected_lift: { level: 'low' | 'medium' | 'high'; metric: string };
  confidence: 'Low' | 'Medium' | 'High';
  confidence_justification: string[];
  risks: string[];
  assets_needed: string[];
  suggested_execution_steps: string[];
};

export type GenerationMetadata = {
  model: string;
  embed_model: string;
  embed_ms: number;
  citations: Citation[];
};

export type Run = {
  domain: string;
  url?: string;
  timestamp: string; // ISO
  signals: Record<string, string[]>; // evidence buckets
  error?: string;
};

export type TelemetryEvent = {
  run_id: string;              // `${domain}__${timestamp}`
  user_email?: string;
  action: 'generate_pack' | 'approve' | 'create_pr';
  timestamp: string;           // ISO
};
```

---

## JSON Schemas (for API validation)

DecisionPack schema (request/response):
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://growthsignal/schemas/decision_pack.json",
  "type": "object",
  "required": ["title","hypothesis","expected_lift","confidence","confidence_justification","risks","assets_needed","suggested_execution_steps"],
  "properties": {
    "title": {"type": "string"},
    "hypothesis": {"type": "string"},
    "expected_lift": {
      "type": "object",
      "required": ["level","metric"],
      "properties": {
        "level": {"type": "string", "enum": ["low","medium","high"]},
        "metric": {"type": "string"}
      }
    },
    "confidence": {"type": "string", "enum": ["Low","Medium","High"]},
    "confidence_justification": {"type": "array", "items": {"type": "string"}},
    "risks": {"type": "array", "items": {"type": "string"}},
    "assets_needed": {"type": "array", "items": {"type": "string"}},
    "suggested_execution_steps": {"type": "array", "items": {"type": "string"}}
  }
}
```

Run schema:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://growthsignal/schemas/run.json",
  "type": "object",
  "required": ["domain","timestamp","signals"],
  "properties": {
    "domain": {"type": "string"},
    "url": {"type": "string"},
    "timestamp": {"type": "string"},
    "signals": {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string"}}},
    "error": {"type": "string"}
  }
}
```

Create PR response schema:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://growthsignal/schemas/create_pr_response.json",
  "type": "object",
  "required": ["success","mode","message","branch"],
  "properties": {
    "success": {"type": "boolean"},
    "mode": {"type": "string", "enum": ["pr_created","preview"]},
    "message": {"type": "string"},
    "url": {"type": "string"},
    "branch": {"type": "string"}
  }
}
```

---

## Pages

### Dashboard → `pages/index.jsx`
UI: metrics (last run time, extracted signals), list of runs with link to run detail.

Data sources:
- GET `/api/runs` → list of `Run`

Wireframe outline:
```jsx
export default function Dashboard() {
  // fetch runs client-side or getServerSideProps
  // compute lastRunTime, signalsCount
  // render cards + list linking to /run/[id]
}
```

### Run Detail → `pages/run/[id].jsx`
UI: left EvidenceList, center DecisionPackEditor, right AssetPreview; ApproveModal on approve.

Data sources:
- GET `/api/runs?id={id}` → single `Run`
- POST `/api/generate-pack` → { pack: DecisionPack, metadata: GenerationMetadata }
- POST `/api/create-pr` → create PR or preview

Wireframe outline:
```jsx
export default function RunDetail() {
  // fetch run by id
  // local state: pack, metadata, assets (lp/emails/linkedin), auth state
  // on Generate: call /api/generate-pack; update state
  // on Approve: open ApproveModal; on confirm call /api/create-pr
}
```

---

## Components

### EvidenceList.tsx
Props:
```ts
type EvidenceListProps = {
  signals: Record<string, string[]>; // from Run.signals
  className?: string;
};
```
Behavior:
- Render expandable sections for each key in `signals`
- Scrollable list items

### DecisionPackEditor.tsx
Props:
```ts
type DecisionPackEditorProps = {
  value: DecisionPack;
  onChange: (next: DecisionPack) => void;
  metadata?: GenerationMetadata; // show model, embed_ms, citations
  onGenerate?: () => Promise<void>; // triggers API call
  disabled?: boolean;
  className?: string;
};
```
Behavior:
- Edits `DecisionPack` fields
- Button “Auto-generate Decision Pack” calls `onGenerate`
- Shows citations if provided

### AssetPreview.tsx
Props:
```ts
type AssetPreviewProps = {
  lpSnippet: string;
  emails: string;
  linkedin: string;
  onChange: (next: { lpSnippet: string; emails: string; linkedin: string }) => void;
  className?: string;
};
```
Behavior:
- Three textareas for LP, emails, LinkedIn copy

### ApproveModal.tsx
Props:
```ts
type ApproveModalProps = {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  requiresAuth?: boolean;
  isAuthed: boolean;
  onAuthSubmit?: (email: string, password: string) => Promise<boolean>; // compare with NEXT_DEMO_PASSWORD
};
```
Behavior:
- If not authed, show email + password fields and a Sign in button
- Show confirm text and "Create PR now" primary button

---

## API Routes

All routes should enforce auth for privileged operations. Suggested header for demo auth:
- `x-demo-auth: <password>` (must equal `process.env.NEXT_DEMO_PASSWORD`)

Optionally include telemetry header values; or the server can derive from body.

### GET /api/runs
- List runs or return a single run by `id`

Query params:
- `id` (optional): domain or run_id (`domain__timestamp`)

Responses:
```json
// 200 list
[
  {
    "domain": "techcrunch.com",
    "url": "https://techcrunch.com/startups",
    "timestamp": "2025-08-25T06:37:29Z",
    "signals": {"headlines_paragraphs": ["...", "..."]}
  }
]
```
```json
// 200 single
{
  "domain": "techcrunch.com",
  "url": "https://techcrunch.com/startups",
  "timestamp": "2025-08-25T06:37:29Z",
  "signals": {"headlines_paragraphs": ["...", "..."]}
}
```

Errors:
- 404 if not found

Implementation note: This can proxy to Python files under `Signal_Miner/output/*.json` or keep a mirrored store.

### POST /api/generate-pack
Generates a `DecisionPack` via backend RAG.

Request body:
```json
{
  "runId": "techcrunch.com__2025-08-25T06:37:29Z",
  "model": "gpt-4o-mini",
  "embed_model": "text-embedding-3-small"
}
```

Response:
```json
{
  "pack": {
    "title": "Growth Experiment Title",
    "hypothesis": "...",
    "expected_lift": {"level": "medium", "metric": "conversion rate"},
    "confidence": "Medium",
    "confidence_justification": ["..."],
    "risks": ["..."],
    "assets_needed": ["..."],
    "suggested_execution_steps": ["..."]
  },
  "metadata": {
    "model": "gpt-4o-mini",
    "embed_model": "text-embedding-3-small",
    "embed_ms": 312,
    "citations": [
      {"score": 0.83, "snippet": "...", "source_url": "https://...", "snapshot_file": "...html"}
    ]
  }
}
```

Errors:
- 400 invalid `runId`
- 500 backend failure

Telemetry:
- Server should log `{ action: 'generate_pack', run_id, user_email?, timestamp }` to a local store or forward to Python.

### POST /api/create-pr
Creates a GitHub PR or writes a preview, mirroring Python `executor.pr_executor.preview_or_create_pr`.

Headers:
- `x-demo-auth` required (matches `NEXT_DEMO_PASSWORD`)

Request body:
```json
{
  "runId": "techcrunch.com__2025-08-25T06:37:29Z",
  "pack": { /* DecisionPack */ },
  "assets": {
    "lp_html": "<html>...",
    "emails": "...",
    "linkedin": "..."
  },
  "github": {
    "token": "optional token",
    "repo": "owner/repo"
  },
  "user_email": "optional@example.com"
}
```

Response (success):
```json
{
  "success": true,
  "mode": "pr_created",
  "message": "Pull Request created",
  "url": "https://github.com/owner/repo/pull/123",
  "branch": "play/slug-20250825T063729Z"
}
```
or
```json
{
  "success": true,
  "mode": "preview",
  "message": "Preview saved",
  "url": "/output/previews/slug_pr_preview.json",
  "branch": "play/slug-20250825T063729Z"
}
```

Errors:
- 401 if `x-demo-auth` missing/incorrect
- 400 invalid payload
- 500 backend failure

Telemetry:
- Log `{ action: 'approve' }` on modal confirm
- Log `{ action: 'create_pr' }` after success (both modes)

---

## Example fetch wrappers (client)
```ts
// lib/api.ts
export async function fetchRuns(id?: string) {
  const q = id ? `?id=${encodeURIComponent(id)}` : '';
  const res = await fetch(`/api/runs${q}`);
  if (!res.ok) throw new Error('Failed to load runs');
  return res.json();
}

export async function generatePack(runId: string) {
  const res = await fetch('/api/generate-pack', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ runId })
  });
  if (!res.ok) throw new Error('Failed to generate pack');
  return res.json();
}

export async function createPr(payload: any, demoPassword: string) {
  const res = await fetch('/api/create-pr', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'x-demo-auth': demoPassword },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Failed to create PR');
  return res.json();
}
```

---

## Example cURL requests

List runs:
```bash
curl -s http://localhost:3000/api/runs | jq
```

Generate pack:
```bash
curl -s -X POST http://localhost:3000/api/generate-pack \
  -H 'Content-Type: application/json' \
  -d '{"runId":"techcrunch.com__2025-08-25T06:37:29Z"}' | jq
```

Create PR (preview without token):
```bash
curl -s -X POST http://localhost:3000/api/create-pr \
  -H 'Content-Type: application/json' \
  -H 'x-demo-auth: YOUR_DEMO_PASSWORD' \
  -d '{
    "runId":"techcrunch.com__2025-08-25T06:37:29Z",
    "pack": {"title":"..","hypothesis":"..","expected_lift":{"level":"medium","metric":"CR"},"confidence":"Medium","confidence_justification":[],"risks":[],"assets_needed":[],"suggested_execution_steps":[]},
    "assets": {"lp_html":"<html>..</html>","emails":"..","linkedin":".."},
    "github": {"repo":"owner/repo"}
  }' | jq
```

---

## Tailwind UI notes
- Use a light, calm palette (gray-50 background, white cards, rounded-xl, shadow-sm)
- Spacing: generous padding (p-6 to p-10), gaps between columns (gap-8)
- Typography: `font-sans` with tracking-wide for headings
- Components should be responsive with a 3-column layout on lg screens and stacked on mobile

---

## Auth considerations
- Gate the Approve/PR actions in the client (show modal requiring password)
- Enforce auth on the server in `/api/create-pr` by checking `x-demo-auth`
- Do not store tokens client-side; pass `github.token` only on submit

---

## Implementation notes
- If integrating directly with the existing Python backend, the API routes can proxy to it (e.g., using `node-fetch` to call Flask/FastAPI endpoints). Otherwise, re-implement minimal logic server-side in Next.js.
- Keep telemetry in a simple JSON file server-side (Node) or forward to the Python telemetry writer for consistency with the Streamlit version.


