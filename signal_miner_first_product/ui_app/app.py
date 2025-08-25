import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

import streamlit as st

# Add the Signal_Miner directory to path so we can import the RAG module
SIGNAL_MINER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Signal_Miner"))
sys.path.insert(0, SIGNAL_MINER_PATH)

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Signal_Miner", "output"))
TELEMETRY_PATH = os.path.join(OUTPUT_DIR, "telemetry.json")


def _get_demo_password() -> str:
    try:
        return st.secrets.get("demo_password", "")
    except Exception:
        return ""


def _log_telemetry(action: str, run: Dict[str, Any], user_email: str = "") -> None:
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        events = []
        if os.path.exists(TELEMETRY_PATH):
            with open(TELEMETRY_PATH, "r", encoding="utf-8") as f:
                try:
                    events = json.load(f) or []
                except Exception:
                    events = []
        run_id = f"{run.get('domain','unknown')}__{run.get('timestamp','')}"
        events.append({
            "run_id": run_id,
            "user_email": user_email or st.session_state.get("user_email", ""),
            "action": action,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })
        with open(TELEMETRY_PATH, "w", encoding="utf-8") as f:
            json.dump(events, f, indent=2)
    except Exception:
        # Best-effort; do not break UI on telemetry errors
        pass


def load_combined() -> List[Dict[str, Any]]:
    combined_path = os.path.join(OUTPUT_DIR, "signals.json")
    if os.path.exists(combined_path):
        with open(combined_path, "r", encoding="utf-8") as f:
            return json.load(f)
    # Fallback: read all *.json files excluding signals.json
    items = []
    for fname in os.listdir(OUTPUT_DIR):
        if not fname.endswith(".json"):
            continue
        if fname == "signals.json":
            continue
        with open(os.path.join(OUTPUT_DIR, fname), "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                items.append(data)
            except Exception:
                continue
    return items


def card(title: str, body: str, key: str):
    with st.container(border=True):
        st.subheader(title)
        st.write(body)


def page_dashboard():
    st.title("GrowthSignal Dashboard")
    st.caption("Ship evidence-backed growth experiments in 48 hours.")

    data = load_combined()
    last_run_time = None
    signals_count = 0
    for item in data:
        ts = item.get("timestamp")
        if ts:
            try:
                t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                if last_run_time is None or t > last_run_time:
                    last_run_time = t
            except Exception:
                pass
        signals = item.get("signals", {})
        for k, v in signals.items():
            if isinstance(v, list):
                signals_count += len(v)

    cols = st.columns(3)
    with cols[0]:
        card("Last run", last_run_time.isoformat() if last_run_time else "—", "last_run")
    with cols[1]:
        card("Extracted signals", f"{signals_count}", "sig_count")
    with cols[2]:
        if st.button("Run miner", use_container_width=True):
            st.info("Run miner from terminal: python Signal_Miner/signal_miner.py")

    st.markdown("### Last runs")
    for item in data:
        domain = item.get("domain", "unknown")
        ts = item.get("timestamp", "—")
        error = item.get("error")
        with st.container(border=True):
            st.write(f"**{domain}**  ")
            st.write(f"Time: {ts}")
            if error:
                st.warning(f"Error: {error}")
            if st.button("View run", key=f"view-{domain}"):
                st.session_state["selected_run"] = domain
                st.session_state["page"] = "detail"
                st.experimental_rerun()


def load_run(domain: str) -> Dict[str, Any]:
    safe_name = domain.replace("/", "_")
    path = os.path.join(OUTPUT_DIR, f"{safe_name}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    # fallback: best-effort
    data = load_combined()
    for item in data:
        if item.get("domain") == domain:
            return item
    return {}


def page_detail():
    domain = st.session_state.get("selected_run")
    if not domain:
        st.info("Select a run from Dashboard.")
        if st.button("Back to Dashboard"):
            st.session_state["page"] = "dashboard"
            st.experimental_rerun()
        return

    run = load_run(domain)
    st.title(f"Run: {domain}")
    st.caption(run.get("url", ""))

    # --- Auth Gate for Approvals ---
    if "authed" not in st.session_state:
        st.session_state["authed"] = False
    if "user_email" not in st.session_state:
        st.session_state["user_email"] = ""

    with st.expander("Authentication (demo)", expanded=not st.session_state["authed"]):
        st.write("Enter the demo password to unlock Approve actions.")
        demo_pw = _get_demo_password()
        email = st.text_input("Email (optional)", value=st.session_state.get("user_email", ""))
        pw = st.text_input("Password", type="password")
        if st.button("Sign in"):
            if demo_pw and pw == demo_pw:
                st.session_state["authed"] = True
                st.session_state["user_email"] = email.strip()
                st.success("Signed in.")
            else:
                st.error("Invalid password. Check Streamlit secrets.")

    col_left, col_center, col_right = st.columns([1.1, 1.5, 1.2], gap="large")

    with col_left:
        st.subheader("Evidence")
        signals = run.get("signals", {})
        for key, items in signals.items():
            with st.expander(key, expanded=True):
                for i, it in enumerate(items):
                    snippet = "; ".join(it) if isinstance(it, list) else str(it)
                    st.write(f"{i+1}. {snippet}")

    with col_center:
        st.subheader("Decision Pack")
        
        # Auto-generate button
        if st.button("🚀 Auto-generate Decision Pack", type="primary"):
            try:
                # Show loading state
                with st.spinner("Generating Decision Pack..."):
                    # Import the RAG module
                    from rfg.generate_pack import generate_pack_for_run
                    
                    # Get the run file path
                    safe_name = domain.replace("/", "_")
                    run_path = os.path.join(OUTPUT_DIR, f"{safe_name}.json")
                    
                    if not os.path.exists(run_path):
                        st.error(f"Run file not found: {run_path}")
                        return
                    
                    # Generate the pack
                    result = generate_pack_for_run(run_path)
                    pack = result["pack"]
                    metadata = result["metadata"]
                    
                    # Store in session state
                    pack_key = f"pack-{domain}"
                    st.session_state[pack_key] = pack
                    st.session_state[f"metadata-{domain}"] = metadata
                    
                    st.success("Decision Pack generated successfully!")
                    _log_telemetry("generate_pack", run)
                    
                    # Show metadata
                    with st.expander("Generation Details", expanded=True):
                        st.write(f"**Model:** {metadata['model']}")
                        st.write(f"**Embedding Model:** {metadata['embed_model']}")
                        st.write(f"**Embedding Time:** {metadata['embed_ms']}ms")
                        
                        st.write("**Top Citations:**")
                        for i, citation in enumerate(metadata['citations'][:5], 1):
                            st.write(f"{i}. Score: {citation['score']:.3f} | {citation['snippet']}")
                
                st.experimental_rerun()
                
            except Exception as e:
                st.error(f"Generation failed: {str(e)}")
                st.info("Please check your OPENAI_API_KEY environment variable and try again, or edit manually.")
        
        # Show generation metadata if available
        metadata_key = f"metadata-{domain}"
        if metadata_key in st.session_state:
            metadata = st.session_state[metadata_key]
            with st.expander("Last Generation", expanded=False):
                st.write(f"Model: {metadata['model']} | Embeddings: {metadata['embed_ms']}ms")
                st.write("Citations:")
                for i, citation in enumerate(metadata['citations'][:3], 1):
                    st.write(f"{i}. {citation['snippet'][:80]}...")

        default_pack = {
            "title": "", "hypothesis": "", "expected_lift": {"level": "medium", "metric": ""}, 
            "confidence": "Medium", "confidence_justification": [], "risks": [], 
            "assets_needed": [], "suggested_execution_steps": []
        }
        pack_key = f"pack-{domain}"
        pack = st.session_state.get(pack_key, default_pack)
        
        pack["title"] = st.text_input("Title", value=pack.get("title", ""))
        pack["hypothesis"] = st.text_area("Hypothesis", value=pack.get("hypothesis", ""), height=120)
        
        # Expected lift
        left1, right1 = st.columns(2)
        with left1:
            lift_level = st.selectbox("Expected Lift Level", ["low", "medium", "high"], 
                                    index=["low", "medium", "high"].index(pack.get("expected_lift", {}).get("level", "medium")))
        with right1:
            lift_metric = st.text_input("Metric", value=pack.get("expected_lift", {}).get("metric", ""))
        pack["expected_lift"] = {"level": lift_level, "metric": lift_metric}
        
        pack["confidence"] = st.select_slider("Confidence", options=["Low","Medium","High"], 
                                            value=pack.get("confidence", "Medium"))
        
        # Arrays
        pack["confidence_justification"] = st.text_area("Confidence Justification (one per line)", 
                                                       value="\n".join(pack.get("confidence_justification", [])), height=80)
        pack["risks"] = st.text_area("Risks (one per line)", 
                                   value="\n".join(pack.get("risks", [])), height=80)
        pack["assets_needed"] = st.text_area("Assets Needed (one per line)", 
                                           value="\n".join(pack.get("assets_needed", [])), height=80)
        pack["suggested_execution_steps"] = st.text_area("Execution Steps (one per line)", 
                                                        value="\n".join(pack.get("suggested_execution_steps", [])), height=100)
        
        # Convert text areas back to lists
        pack["confidence_justification"] = [line.strip() for line in pack["confidence_justification"].split("\n") if line.strip()]
        pack["risks"] = [line.strip() for line in pack["risks"].split("\n") if line.strip()]
        pack["assets_needed"] = [line.strip() for line in pack["assets_needed"].split("\n") if line.strip()]
        pack["suggested_execution_steps"] = [line.strip() for line in pack["suggested_execution_steps"].split("\n") if line.strip()]
        
        st.session_state[pack_key] = pack
        
        # Save button
        if st.button("💾 Save Decision Pack"):
            try:
                from rfg.generate_pack import save_pack
                outfile = save_pack(pack, domain)
                st.success(f"Saved to: {outfile}")
            except Exception as e:
                st.error(f"Save failed: {str(e)}")

    with col_right:
        st.subheader("Assets")
        lp = st.text_area("LP snippet", height=140)
        emails = st.text_area("3-email sequence", height=200)
        linkedin = st.text_area("LinkedIn copy", height=120)

        # GitHub configuration
        st.markdown("---")
        st.subheader("GitHub Configuration")
        github_token = st.text_input("GitHub Token (optional)", type="password", 
                                   help="Required to create actual PRs. Get from GitHub Settings > Developer settings > Personal access tokens")
        github_repo = st.text_input("GitHub Repository", 
                                  placeholder="owner/repo", 
                                  help="Repository where PR will be created (e.g., 'yourusername/demo-repo')")
        
        # Gate Approve action behind auth
        disabled_approve = not st.session_state.get("authed", False)
        if disabled_approve:
            st.info("Sign in above to enable Approve actions.")

        if st.button("🚀 Approve & Create PR", type="primary", disabled=disabled_approve):
            # Confirmation modal
            with st.modal("Confirm PR Creation"):
                st.write("You're about to create a PR with the current Decision Pack and LP snippet.")
                st.write("Make sure the content is ready.")
                confirm = st.button("Create PR now", type="primary")
                cancel = st.button("Cancel")
                if not confirm:
                    st.stop()
            _log_telemetry("approve", run)
            try:
                # First save the decision pack if not already saved
                pack_key = f"pack-{domain}"
                pack = st.session_state.get(pack_key, {})
                
                if not pack.get("title"):
                    st.error("Please fill in the Decision Pack fields first")
                    return
                
                # Save pack to file
                from rfg.generate_pack import save_pack
                pack_path = save_pack(pack, domain)
                
                # Generate landing page HTML from LP snippet
                lp_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{pack.get('title', 'Growth Experiment')}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               line-height: 1.6; margin: 0; padding: 20px; background: #fafafa; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 40px; 
                    border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        h1 {{ color: #111827; margin-bottom: 20px; }}
        .lp-content {{ background: #f9fafb; padding: 20px; border-radius: 8px; 
                     border-left: 4px solid #0A84FF; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{pack.get('title', 'Growth Experiment')}</h1>
        <div class="lp-content">
            {lp if lp else '<p>Landing page content will be added here.</p>'}
        </div>
        <p><em>Generated by GrowthSignal</em></p>
    </div>
</body>
</html>"""
                
                # Call PR executor
                from executor.pr_executor import preview_or_create_pr
                
                with st.spinner("Creating PR..."):
                    result = preview_or_create_pr(
                        pack_path=pack_path,
                        lp_html=lp_html,
                        domain=domain,
                        github_token=github_token if github_token else None,
                        github_repo=github_repo if github_repo else None
                    )
                
                if result["success"]:
                    if result["mode"] == "pr_created":
                        st.success(f"✅ {result['message']}")
                        st.markdown(f"**PR URL:** [{result['url']}]({result['url']})")
                        st.info(f"Branch: `{result['branch']}`")
                        _log_telemetry("create_pr", run)
                    else:
                        st.success(f"✅ {result['message']}")
                        st.info(f"Preview saved to: `{result['url']}`")
                        st.info(f"Branch: `{result['branch']}`")
                        if not github_token:
                            st.warning("To create actual PRs, add your GitHub token above")
                        _log_telemetry("create_pr", run)
                else:
                    st.error(f"❌ {result['message']}")
                    
            except Exception as e:
                st.error(f"Failed to create PR: {str(e)}")
                st.info("Check your GitHub token and repository settings")

    if st.button("Back to Dashboard"):
        st.session_state["page"] = "dashboard"
        st.experimental_rerun()


def page_settings():
    st.title("Settings")
    st.caption("Configuration for miner and APIs")

    allowed_domains_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Signal_Miner", "url.txt"))
    apis_path = os.path.join(OUTPUT_DIR, "api_keys.json")

    st.subheader("Allowlist URLs")
    allow_text = ""
    if os.path.exists(allowed_domains_path):
        with open(allowed_domains_path, "r", encoding="utf-8") as f:
            allow_text = f.read()
    allow_text_new = st.text_area("One URL per line", value=allow_text, height=200)
    if st.button("Save allowlist"):
        with open(allowed_domains_path, "w", encoding="utf-8") as f:
            f.write(allow_text_new)
        st.success("Saved allowlist.")

    st.subheader("API Keys")
    key_openai = st.text_input("OpenAI API Key", type="password")
    key_pinecone = st.text_input("Pinecone API Key", type="password")
    key_github = st.text_input("GitHub Token", type="password")
    if st.button("Save API keys"):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(apis_path, "w", encoding="utf-8") as f:
            json.dump({"openai": key_openai, "pinecone": key_pinecone, "github": key_github}, f, indent=2)
        st.success("Saved API keys (local only).")


def main():
    st.set_page_config(page_title="GrowthSignal", page_icon="🚀", layout="wide")

    tabs = st.sidebar.radio("Navigate", ["Dashboard", "Run detail", "Settings"])  # simple routing
    if tabs == "Dashboard":
        st.session_state["page"] = "dashboard"
        page_dashboard()
    elif tabs == "Run detail":
        st.session_state["page"] = "detail"
        page_detail()
    else:
        st.session_state["page"] = "settings"
        page_settings()


if __name__ == "__main__":
    main()
