from __future__ import annotations

from html import escape
import os
from textwrap import dedent

import requests
import streamlit as st

try:
    from frontend.workflow_state import next_action, workflow_progress, workflow_steps
except ModuleNotFoundError:
    from workflow_state import next_action, workflow_progress, workflow_steps


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
API_BASE_URL_FALLBACKS = os.getenv("API_BASE_URL_FALLBACKS", "")
DEFAULT_REQUEST_TIMEOUT_SECONDS = int(os.getenv("API_REQUEST_TIMEOUT_SECONDS", "30"))
LLM_REQUEST_TIMEOUT_SECONDS = int(os.getenv("LLM_REQUEST_TIMEOUT_SECONDS", "300"))

QUESTION_AGENT_STEPS = [
    ("Input Gathering Agent", "Reads the book idea and decides what context is missing."),
    ("Gemini", "Turns the idea into adaptive questions for the author."),
    ("Checkpoint Service", "Saves the questions and records the workflow run."),
]
BOOK_PLAN_AGENT_STEPS = [
    ("Input Understanding Agent", "Extracts audience, goals, tone, constraints, and source preferences from the answers."),
    ("Book Strategy Agent", "Chooses positioning, reader promise, learning path, and differentiation."),
    ("Structure Designer Agent", "Builds the parts, chapters, outcomes, and approval-ready outline."),
    ("Checkpoint Service", "Stores the plan so the next agent can continue from the same state."),
]
STRUCTURE_REVISION_AGENT_STEPS = [
    ("Human Feedback Gate", "Captures the revision request and locks chapter generation."),
    ("Structure Designer Agent", "Revises the existing outline using the latest feedback."),
    ("Gemini", "Applies the requested structure change while preserving usable parts."),
    ("Checkpoint Service", "Stores the revised structure and revision run metadata."),
]
CHAPTER_AGENT_STEPS = [
    ("Chapter Planner Agent", "Selects the chapter objective, key concepts, examples, and exercises."),
    ("Chapter Writer Agent", "Drafts the chapter from the approved structure and project memory."),
    ("Technical Reviewer Agent", "Checks technical accuracy, gaps, and implementation clarity."),
    ("Editor Agent", "Rewrites the draft into the final chapter markdown."),
    ("Checkpoint Service", "Stores the final chapter and run metadata."),
]
WORKFLOW_STEP_DETAILS = {
    "Project": "Workspace and book idea",
    "Questions": "Adaptive author inputs",
    "Brief": "Audience, goals, constraints",
    "Strategy": "Positioning and learning path",
    "Structure": "Parts, chapters, outcomes",
    "Approved": "Human approval gate",
    "Chapter": "Generated markdown draft",
}

st.set_page_config(page_title="Agentic Book Creator", layout="wide")
st.title("Agentic Book Creator")
st.markdown(
    dedent(
        """
    <style>
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] .workflow-panel {
        border: 1px solid rgba(148, 163, 184, 0.24);
        border-radius: 12px;
        padding: 14px;
        background: rgba(15, 23, 42, 0.36);
        margin: 10px 0 14px;
    }
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] .workflow-kicker {
        color: rgba(226, 232, 240, 0.68);
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] .workflow-step {
        display: grid;
        grid-template-columns: 30px minmax(0, 1fr);
        gap: 10px;
        align-items: start;
        padding: 10px;
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 10px;
        margin-bottom: 8px;
        background: rgba(30, 41, 59, 0.34);
    }
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] .workflow-step.done {
        border-color: rgba(34, 197, 94, 0.42);
        background: rgba(22, 101, 52, 0.16);
    }
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] .workflow-step.active {
        border-color: rgba(96, 165, 250, 0.58);
        background: rgba(30, 64, 175, 0.22);
        box-shadow: inset 3px 0 0 rgba(96, 165, 250, 0.9);
    }
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] .workflow-marker {
        width: 26px;
        height: 26px;
        border-radius: 999px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: #cbd5e1;
        background: rgba(148, 163, 184, 0.16);
        font-size: 0.76rem;
        font-weight: 800;
    }
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] .workflow-step.done .workflow-marker {
        color: #dcfce7;
        background: rgba(34, 197, 94, 0.34);
    }
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] .workflow-step.active .workflow-marker {
        color: #eff6ff;
        background: rgba(59, 130, 246, 0.88);
    }
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] .workflow-label {
        color: #f8fafc;
        font-size: 0.95rem;
        font-weight: 760;
        line-height: 1.15;
        margin-bottom: 3px;
    }
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] .workflow-desc {
        color: rgba(226, 232, 240, 0.62);
        font-size: 0.76rem;
        line-height: 1.25;
    }
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] .workflow-pill {
        display: inline-block;
        color: #bfdbfe;
        background: rgba(37, 99, 235, 0.22);
        border: 1px solid rgba(96, 165, 250, 0.24);
        border-radius: 999px;
        padding: 3px 8px;
        font-size: 0.68rem;
        font-weight: 760;
        margin-top: 7px;
    }
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] .workflow-next {
        border: 1px solid rgba(96, 165, 250, 0.32);
        border-radius: 12px;
        padding: 12px;
        background: rgba(37, 99, 235, 0.18);
        color: #dbeafe;
        margin: 8px 0 12px;
        line-height: 1.35;
        font-size: 0.86rem;
    }
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] .workflow-id {
        color: rgba(226, 232, 240, 0.74);
        font-size: 0.72rem;
        overflow-wrap: anywhere;
        margin: 0 0 10px;
    }
    </style>
    """
    ),
    unsafe_allow_html=True,
)

if "project_id" not in st.session_state:
    st.session_state.project_id = None
if "project" not in st.session_state:
    st.session_state.project = None

page = st.sidebar.radio(
    "Workspace",
    ["Create Book", "Input Questions", "Book Brief", "Book Strategy", "Book Structure", "Chapter Workspace", "Export"],
)


def api_base_urls() -> list[str]:
    urls = [st.session_state.get("api_base_url") or API_BASE_URL]
    urls.extend(url.strip() for url in API_BASE_URL_FALLBACKS.split(",") if url.strip())
    if "://api:" in API_BASE_URL:
        urls.extend(["http://host.docker.internal:8000", "http://127.0.0.1:8000"])

    deduped = []
    for url in urls:
        normalized = url.rstrip("/")
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return deduped


def api_request(method: str, path: str, payload: dict | None = None, timeout_seconds: int | None = None):
    errors = []
    request_timeout = timeout_seconds or DEFAULT_REQUEST_TIMEOUT_SECONDS
    for base_url in api_base_urls():
        try:
            response = requests.request(method, f"{base_url}{path}", json=payload or None, timeout=request_timeout)
            st.session_state.api_base_url = base_url
            if response.status_code == 409:
                detail = _response_detail(response)
                st.warning(detail)
                st.stop()
            response.raise_for_status()
            return response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
        except requests.HTTPError as exc:
            detail = _response_detail(exc.response) if exc.response is not None else str(exc)
            st.error(detail)
            st.stop()
        except requests.Timeout as exc:
            st.error(
                "The backend accepted the request, but the LLM workflow took longer than the UI waited. "
                "Refresh the project in a moment, or increase `LLM_REQUEST_TIMEOUT_SECONDS` in Docker."
            )
            with st.expander("Timed out request"):
                st.code(f"{base_url}{path}\nWaited {request_timeout} seconds.\n{exc}")
            st.stop()
        except requests.RequestException as exc:
            errors.append(f"{base_url}: {exc}")

    st.error("Could not connect to the FastAPI backend. If you are using Docker, start the full stack with `docker compose up --build`.")
    with st.expander("Connection attempts"):
        for error in errors:
            st.code(error)
    st.stop()


def _response_detail(response: requests.Response) -> str:
    try:
        data = response.json()
    except ValueError:
        return response.text or f"Request failed with status {response.status_code}."
    return data.get("detail") or str(data)


def api_post(path: str, payload: dict | None = None, timeout_seconds: int | None = None):
    return api_request("POST", path, payload, timeout_seconds)


def api_get(path: str):
    return api_request("GET", path)


def api_get_optional(path: str):
    for base_url in api_base_urls():
        try:
            response = requests.get(f"{base_url}{path}", timeout=DEFAULT_REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()
            st.session_state.api_base_url = base_url
            return response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
        except requests.RequestException:
            continue
    return None


def refresh_project():
    if st.session_state.project_id:
        st.session_state.project = api_get(f"/projects/{st.session_state.project_id}")


def ensure_project_loaded():
    if st.session_state.project_id and not _looks_like_project(st.session_state.project):
        refresh_project()


def _looks_like_project(project: dict | None) -> bool:
    return bool(project and project.get("project_id"))


def set_project_artifact(field: str, value):
    ensure_project_loaded()
    if st.session_state.project:
        st.session_state.project[field] = value


def project_label(project: dict) -> str:
    title = project.get("title") or "Untitled book"
    status = project.get("status") or "draft"
    project_id = project.get("project_id", "")
    suffix = project_id[:8] if project_id else "new"
    return f"{title} - {status} - {suffix}"


def restore_project(project: dict):
    st.session_state.project_id = project["project_id"]
    st.session_state.project = project


def saved_answer_map(project: dict | None) -> dict[str, str]:
    return {answer.get("field"): answer.get("answer", "") for answer in (project or {}).get("user_answers", [])}


def render_project_picker():
    projects = api_get_optional("/projects") or []
    if not projects:
        return

    if not st.session_state.project_id:
        restore_project(projects[0])

    options = [project["project_id"] for project in projects]
    current_index = options.index(st.session_state.project_id) if st.session_state.project_id in options else 0
    project_lookup = {project["project_id"]: project for project in projects}

    st.sidebar.caption("Resume project")
    selected_id = st.sidebar.selectbox(
        "Saved projects",
        options,
        index=current_index,
        format_func=lambda project_id: project_label(project_lookup[project_id]),
        label_visibility="collapsed",
    )
    if selected_id != st.session_state.project_id:
        selected_project = api_get_optional(f"/projects/{selected_id}") or project_lookup[selected_id]
        restore_project(selected_project)
        st.rerun()


def render_agent_activity(steps: list[tuple[str, str]]):
    for index, (agent_name, work) in enumerate(steps, start=1):
        st.write(f"{index}. **{agent_name}**")
        st.caption(work)


def render_artifact_summary(summary: dict):
    if not summary:
        return
    labels = [
        ("Questions", summary.get("questions", 0)),
        ("Answers", summary.get("answers", 0)),
        ("Revisions", summary.get("revision_requests", 0)),
        ("Plans", summary.get("chapter_plans", 0)),
        ("Drafts", summary.get("chapter_drafts", 0)),
        ("Reviews", summary.get("chapter_reviews", 0)),
        ("Final chapters", summary.get("final_chapters", 0)),
        ("Checkpoints", summary.get("checkpoints", 0)),
    ]
    cols = st.columns(4)
    for index, (label, value) in enumerate(labels):
        cols[index % 4].metric(label, value)


def render_workflow_nodes(nodes: list[dict]):
    if not nodes:
        st.info("This run does not include node-level metadata yet.")
        return
    for index, node in enumerate(nodes, start=1):
        status = node.get("status", "unknown")
        with st.container(border=True):
            st.markdown(f"**{index}. {node.get('name', 'Workflow node')}**")
            st.caption(f"Status: {status}")
            st.write(node.get("role", "No role description recorded."))
            artifacts = node.get("artifacts", [])
            if artifacts:
                st.markdown("**Artifacts touched**")
                st.table(artifacts)


def render_runtime_warnings(warnings: list[dict]):
    for warning in warnings or []:
        st.error(
            "LLM provider fallback was used for "
            f"`{warning.get('field', 'artifact')}`. "
            f"{warning.get('error_type', 'LLM error')}: {warning.get('message', 'No details returned.')}"
        )


def render_latest_runs(project: dict):
    runs = project.get("execution_runs", [])[-5:]
    if not runs:
        return

    with st.sidebar.expander("Recent agent runs"):
        for run in reversed(runs):
            metadata = run.get("llm_metadata", {})
            provider = metadata.get("llm_provider", "llm")
            model = metadata.get("llm_model_version", "configured model")
            st.caption(f"{run.get('run_type', 'workflow')} - {run.get('status', 'unknown')}")
            st.write(f"{provider} / {model}")


def flatten_structure_chapters(structure: dict) -> list[dict]:
    chapters = []
    for part in structure.get("parts", []):
        part_title = part.get("part_title", "Untitled part")
        for chapter in part.get("chapters", []):
            chapters.append({**chapter, "part_title": part_title})
    return chapters


def structure_metrics(structure: dict) -> dict[str, int]:
    chapters = flatten_structure_chapters(structure or {})
    return {
        "parts": len((structure or {}).get("parts", [])),
        "chapters": len(chapters),
        "sections": sum(len(chapter.get("sections", [])) for chapter in chapters),
        "exercises": sum(len(chapter.get("exercises", [])) for chapter in chapters),
    }


def chapter_title_set(structure: dict) -> set[str]:
    return {chapter.get("title", "Untitled chapter") for chapter in flatten_structure_chapters(structure or {})}


def latest_run(project: dict, run_type: str | None = None) -> dict | None:
    runs = project.get("execution_runs", [])
    if run_type:
        runs = [run for run in runs if run.get("run_type") == run_type]
    return runs[-1] if runs else None


def render_run_summary(run: dict | None):
    if not run:
        st.info("No run metadata was returned for this operation.")
        return

    metadata = run.get("llm_metadata", {})
    col1, col2, col3 = st.columns(3)
    col1.metric("Run", run.get("run_type", "workflow"))
    col2.metric("Status", run.get("status", "unknown"))
    col3.metric("Route", metadata.get("model_route", "unknown"))
    st.caption(f"Provider/model: {metadata.get('llm_provider', 'unknown')} / {metadata.get('llm_model_version', 'unknown')}")
    render_runtime_warnings(metadata.get("runtime_warnings", []))
    st.markdown("**Agent nodes and artifacts**")
    render_workflow_nodes(metadata.get("workflow_nodes", []))
    st.markdown("**Artifact counters**")
    render_artifact_summary(metadata.get("artifact_summary", {}))


def render_structure_delta(before: dict, after: dict):
    before_metrics = structure_metrics(before)
    after_metrics = structure_metrics(after)
    rows = []
    for key in ["parts", "chapters", "sections", "exercises"]:
        rows.append(
            {
                "metric": key,
                "before": before_metrics[key],
                "after": after_metrics[key],
                "delta": after_metrics[key] - before_metrics[key],
            }
        )
    st.subheader("What changed")
    st.table(rows)
    before_titles = chapter_title_set(before)
    after_titles = chapter_title_set(after)
    added = sorted(after_titles - before_titles)
    removed = sorted(before_titles - after_titles)
    change_summary = after.get("change_summary")
    last_revision = after.get("last_revision_applied")
    llm_runtime = after.get("llm_runtime", {})
    has_metric_delta = any(row["delta"] for row in rows)

    if llm_runtime.get("status") == "fallback_used":
        st.error(
            "The LLM call failed, so the workflow used the local fallback. "
            f"{llm_runtime.get('error_type', 'LLM error')}: {llm_runtime.get('message', 'No details returned.')}"
        )
    if change_summary:
        st.info(change_summary)
    if last_revision:
        st.caption(f"Latest revision request: {last_revision}")

    if added or removed:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Added chapters**")
            if added:
                for title in added:
                    st.write(f"- {title}")
            else:
                st.caption("No added chapters.")
        with col2:
            st.markdown("**Removed chapters**")
            if removed:
                for title in removed:
                    st.write(f"- {title}")
            else:
                st.caption("No removed chapters.")
    elif not has_metric_delta:
        st.warning(
            "No visible structure delta was detected. The LLM returned a valid structure, "
            "but it did not change the chapter, section, or exercise counts or chapter titles."
        )


def render_structure_overview(structure: dict):
    if not structure:
        st.info("No book structure has been generated yet. Submit the input answers first.")
        return

    project = st.session_state.project or {}
    chapters = flatten_structure_chapters(structure)
    col1, col2, col3 = st.columns(3)
    col1.metric("Parts", len(structure.get("parts", [])))
    col2.metric("Chapters", len(chapters))
    col3.metric("Approval", "Approved" if project.get("structure_approved") else "Pending")

    st.subheader(structure.get("book_title", "Book structure"))
    for part_index, part in enumerate(structure.get("parts", []), start=1):
        st.markdown(f"### Part {part_index}: {part.get('part_title', 'Untitled part')}")
        st.caption(part.get("part_goal", "No part goal provided."))
        for chapter in part.get("chapters", []):
            chapter_number = chapter.get("chapter_number", "?")
            title = chapter.get("title", "Untitled chapter")
            with st.expander(f"Chapter {chapter_number}: {title}", expanded=chapter_number == 1):
                st.write(chapter.get("goal", "No chapter goal provided."))
                sections = chapter.get("sections", [])
                if sections:
                    st.markdown("**Sections**")
                    for section in sections:
                        st.write(f"- {section.get('title', 'Untitled section')}: {section.get('purpose', 'No purpose provided.')}")
                st.markdown("**Practical example**")
                st.write(chapter.get("practical_example", "Not specified."))
                st.markdown("**Mini project**")
                st.write(chapter.get("mini_project", "Not specified."))
                exercises = chapter.get("exercises", [])
                if exercises:
                    st.markdown("**Exercises**")
                    for exercise in exercises:
                        st.write(f"- {exercise}")


def render_book_plan_summary(project: dict):
    st.subheader("Generated Plan")
    brief, strategy, structure = st.tabs(["Brief", "Strategy", "Structure"])
    with brief:
        st.json(project.get("book_requirements", {}))
    with strategy:
        st.json(project.get("book_strategy", {}))
    with structure:
        render_structure_overview(project.get("book_structure", {}))
    render_workflow_debug(project, project.get("book_structure", {}))


def render_operation_payload(title: str, endpoint: str, payload: dict):
    with st.expander(title, expanded=True):
        st.code(endpoint, language="text")
        st.json(payload)


def render_saved_answers(project: dict):
    answers = project.get("user_answers", [])
    if not answers:
        return
    with st.expander("Saved answers", expanded=True):
        for answer in answers:
            st.write(f"**{answer.get('field', 'field')}**")
            st.caption(answer.get("answer", ""))


def render_workflow_debug(project: dict, structure: dict | None = None):
    st.subheader("Agent Execution Trace")
    st.caption("Inspect the LangGraph nodes, provider route, produced artifacts, and the state the next agent will receive.")

    latest_runs = project.get("execution_runs", [])[-8:]
    if latest_runs:
        st.markdown("**Recent runs**")
        for run in reversed(latest_runs):
            metadata = run.get("llm_metadata", {})
            with st.expander(f"{run.get('run_type', 'workflow')} - {run.get('status', 'unknown')}", expanded=False):
                col1, col2, col3 = st.columns(3)
                col1.metric("Provider", metadata.get("llm_provider", "unknown"))
                col2.metric("Model", metadata.get("llm_model_version", "unknown"))
                col3.metric("Route", metadata.get("model_route", "unknown"))
                render_runtime_warnings(metadata.get("runtime_warnings", []))
                render_workflow_nodes(metadata.get("workflow_nodes", []))
                st.markdown("**Run metadata JSON**")
                st.json(metadata)
    else:
        st.info("No workflow runs have been recorded for this project yet.")

    revision_requests = project.get("structure_revision_requests", [])
    if revision_requests:
        st.markdown("**Revision requests**")
        for index, request in enumerate(revision_requests, start=1):
            st.write(f"{index}. {request}")

    with st.expander("Current project state", expanded=False):
        st.json(project)
    if structure is not None:
        with st.expander("Raw structure object", expanded=False):
            st.json(structure)


def render_workflow_timeline(project: dict):
    steps = workflow_steps(project)
    active_index = next((index for index, step in enumerate(steps) if not step["complete"]), len(steps) - 1)
    items = []
    for index, step in enumerate(steps):
        label = str(step["label"])
        complete = bool(step["complete"])
        is_active = index == active_index and not complete
        css_class = "done" if complete else "active" if is_active else "pending"
        marker = "OK" if complete else str(index + 1)
        pill = '<div class="workflow-pill">Now</div>' if is_active else ""
        items.append(
            (
                f'<div class="workflow-step {css_class}">'
                f'<div class="workflow-marker">{marker}</div>'
                "<div>"
                f'<div class="workflow-label">{escape(label)}</div>'
                f'<div class="workflow-desc">{escape(WORKFLOW_STEP_DETAILS.get(label, ""))}</div>'
                f"{pill}"
                "</div>"
                "</div>"
            )
        )
    st.sidebar.markdown(
        f'<div class="workflow-panel"><div class="workflow-kicker">Workflow progress</div>{"".join(items)}</div>',
        unsafe_allow_html=True,
    )


def render_project_progress():
    project = st.session_state.project or {}

    st.sidebar.divider()
    st.sidebar.caption("Current project")
    if project.get("project_id") or st.session_state.project_id:
        st.sidebar.markdown(
            f'<div class="workflow-id">{escape(project.get("project_id", st.session_state.project_id))}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.markdown('<div class="workflow-id">No project selected yet</div>', unsafe_allow_html=True)
    st.sidebar.progress(workflow_progress(project))
    render_workflow_timeline(project)
    st.sidebar.markdown(f'<div class="workflow-next">{escape(next_action(project))}</div>', unsafe_allow_html=True)
    render_latest_runs(project)
    if st.sidebar.button("Refresh project", disabled=not bool(st.session_state.project_id)):
        refresh_project()
        st.rerun()


render_project_picker()
render_project_progress()


if page == "Create Book":
    title = st.text_input("Book title", "Building Agentic AI Systems")
    idea = st.text_area(
        "Initial idea",
        "Quero criar um livro sobre agentes de inteligência artificial para developers de automação e RPA. Quero que seja prático, com exemplos, código, analogias e mini projetos.",
        height=180,
    )
    if st.button("Create project", type="primary"):
        with st.status("Starting LangGraph book workflow...", expanded=True) as status:
            st.write("Creating project workspace.")
            project = api_post("/projects", {"title": title, "initial_idea": idea})
            st.session_state.project_id = project["project_id"]
            st.session_state.project = project

            st.write("Generating adaptive questions with Gemini.")
            render_agent_activity(QUESTION_AGENT_STEPS)
            project = api_post(f"/projects/{project['project_id']}/questions", timeout_seconds=LLM_REQUEST_TIMEOUT_SECONDS)
            st.session_state.project = project
            st.markdown("**Completed run**")
            render_run_summary(latest_run(project, "input_gathering"))
            status.update(label="Project ready for input", state="complete")

        st.session_state.project_id = project["project_id"]
        st.session_state.project = project
        st.success(f"Project created: {project['project_id']}")
        st.info(next_action(project))
        st.subheader("Adaptive Questions")
        st.json(project.get("input_questions", []))

if page == "Input Questions":
    if not st.session_state.project_id:
        st.info("Create a project first.")
    else:
        ensure_project_loaded()
        if st.session_state.project:
            render_saved_answers(st.session_state.project)
        if not st.session_state.project.get("input_questions"):
            if st.button("Generate adaptive questions", type="primary"):
                with st.status("Generating adaptive questions with Gemini...", expanded=True) as status:
                    render_agent_activity(QUESTION_AGENT_STEPS)
                    project = api_post(
                        f"/projects/{st.session_state.project_id}/questions",
                        timeout_seconds=LLM_REQUEST_TIMEOUT_SECONDS,
                    )
                    st.markdown("**Completed run**")
                    render_run_summary(latest_run(project, "input_gathering"))
                    status.update(label="Questions generated", state="complete")
                st.session_state.project = project
                st.rerun()

    if st.session_state.project and st.session_state.project.get("input_questions"):
        st.info(next_action(st.session_state.project))
        saved_answers = saved_answer_map(st.session_state.project)
        answers = []
        for question in st.session_state.project["input_questions"]:
            answer_key = f"{st.session_state.project_id}_{question['field']}"
            if answer_key not in st.session_state and question["field"] in saved_answers:
                st.session_state[answer_key] = saved_answers[question["field"]]
            answer = st.text_input(question["question"], key=answer_key)
            if answer:
                answers.append({"field": question["field"], "answer": answer})
        if st.session_state.project.get("book_requirements"):
            st.success("These answers already generated a book plan. Edit any field and submit again to regenerate.")
            render_book_plan_summary(st.session_state.project)
        if answers and st.button("Submit answers / regenerate plan"):
            with st.status("Building book brief, strategy, and structure...", expanded=True) as status:
                render_operation_payload(
                    "Request sent to the book-plan workflow",
                    f"POST /projects/{st.session_state.project_id}/answers",
                    {"answers": answers},
                )
                render_agent_activity(BOOK_PLAN_AGENT_STEPS)
                project = api_post(
                    f"/projects/{st.session_state.project_id}/answers",
                    {"answers": answers},
                    timeout_seconds=LLM_REQUEST_TIMEOUT_SECONDS,
                )
                st.markdown("**Completed run**")
                render_run_summary(latest_run(project, "book_plan"))
                status.update(label="Book plan generated", state="complete")
            st.session_state.project = project
            st.success("Brief, strategy, and structure generated.")
            st.info(next_action(project))
            render_book_plan_summary(project)

if page == "Book Brief":
    if st.session_state.project_id:
        requirements = api_post(
            f"/projects/{st.session_state.project_id}/requirements",
            timeout_seconds=LLM_REQUEST_TIMEOUT_SECONDS,
        )
        set_project_artifact("book_requirements", requirements)
        st.subheader("Book Brief")
        st.json(requirements)
        if st.session_state.project:
            with st.expander("Debug project state"):
                st.json(st.session_state.project)
    else:
        st.info("Create a project first.")

if page == "Book Strategy":
    if st.session_state.project_id:
        strategy = api_post(
            f"/projects/{st.session_state.project_id}/strategy",
            timeout_seconds=LLM_REQUEST_TIMEOUT_SECONDS,
        )
        set_project_artifact("book_strategy", strategy)
        st.subheader("Book Strategy")
        st.json(strategy)
        if st.session_state.project:
            with st.expander("Debug project state"):
                st.json(st.session_state.project)
    else:
        st.info("Create a project first.")

if page == "Book Structure":
    if not st.session_state.project_id:
        st.info("Create a project first.")
    else:
        ensure_project_loaded()
        structure = api_post(
            f"/projects/{st.session_state.project_id}/structure",
            timeout_seconds=LLM_REQUEST_TIMEOUT_SECONDS,
        )
        set_project_artifact("book_structure", structure)
        project = st.session_state.project or {}

        st.subheader("Book Structure")
        st.caption("Review the outline before the chapter agents are allowed to run.")
        overview_tab, agent_tab, raw_tab = st.tabs(["Overview", "Agent trace", "Raw/debug"])
        with overview_tab:
            render_structure_overview(structure)
        with agent_tab:
            st.markdown("**How this structure was created**")
            render_agent_activity(BOOK_PLAN_AGENT_STEPS)
            st.info("The human approval gate prevents chapter generation until this outline is approved.")
            render_workflow_debug(project, structure)
        with raw_tab:
            st.markdown("**Raw structure JSON**")
            st.json(structure)
            st.markdown("**Full project state**")
            st.json(project)

        st.divider()
        st.subheader("Approval Gate")
        col1, col2 = st.columns(2)
        with col1:
            st.caption("Approve when the outline is good enough for chapter generation.")
            if st.button("Approve structure", type="primary"):
                with st.status("Recording human approval gate...", expanded=True) as status:
                    st.session_state.project = api_post(
                        f"/projects/{st.session_state.project_id}/approve-structure",
                        {"approved": True},
                    )
                    st.markdown("**Completed run**")
                    render_run_summary(latest_run(st.session_state.project, "structure_approval"))
                    status.update(label="Structure approved", state="complete")
                st.success("Structure approved. Chapter agents are now unlocked.")
                st.rerun()
        with col2:
            st.caption("Requesting revision records feedback and keeps the chapter agents locked.")
            revision = st.text_area("Revision request", height=120, placeholder="Example: Make chapters shorter and add more PDF/RAG examples.")
            if st.button("Request revision", disabled=not bool(revision.strip())):
                previous_structure = dict(structure or {})
                revision_payload = {"approved": False, "revision_request": revision.strip()}
                with st.status("Revising structure with agent feedback...", expanded=True) as status:
                    render_operation_payload(
                        "Request sent to the revision workflow",
                        f"POST /projects/{st.session_state.project_id}/approve-structure",
                        revision_payload,
                    )
                    st.markdown("**Structure before revision**")
                    st.table([structure_metrics(previous_structure)])
                    render_agent_activity(STRUCTURE_REVISION_AGENT_STEPS)
                    st.session_state.project = api_post(
                        f"/projects/{st.session_state.project_id}/approve-structure",
                        revision_payload,
                        timeout_seconds=LLM_REQUEST_TIMEOUT_SECONDS,
                    )
                    revised_structure = st.session_state.project.get("book_structure", {})
                    st.markdown("**Structure after revision**")
                    st.table([structure_metrics(revised_structure)])
                    st.markdown("**Completed run**")
                    render_run_summary(latest_run(st.session_state.project, "structure_revision"))
                    status.update(label="Structure revision complete", state="complete")
                st.warning("Revision applied. Review the updated structure before approving.")
                render_structure_delta(previous_structure, st.session_state.project.get("book_structure", {}))
                render_structure_overview(st.session_state.project.get("book_structure", {}))
                render_workflow_debug(st.session_state.project, st.session_state.project.get("book_structure", {}))

if page == "Chapter Workspace":
    if not st.session_state.project_id:
        st.info("Create a project first.")
    else:
        if not st.session_state.project:
            st.session_state.project = api_get(f"/projects/{st.session_state.project_id}")

        structure_approved = bool(st.session_state.project.get("structure_approved"))
        if not structure_approved:
            st.warning("Approve the book structure before generating chapters.")
            if st.button("Approve structure now", type="primary"):
                st.session_state.project = api_post(
                    f"/projects/{st.session_state.project_id}/approve-structure",
                    {"approved": True},
                )
                st.success("Structure approved. You can generate the chapter now.")
                st.rerun()

        chapter_number = st.number_input("Chapter", min_value=1, value=1)
        if st.button("Generate chapter", type="primary", disabled=not structure_approved):
            with st.status("Generating chapter with LangGraph and Gemini...", expanded=True) as status:
                render_agent_activity(CHAPTER_AGENT_STEPS)
                project = api_post(
                    f"/projects/{st.session_state.project_id}/chapters/{chapter_number}/generate",
                    timeout_seconds=LLM_REQUEST_TIMEOUT_SECONDS,
                )
                st.markdown("**Completed run**")
                render_run_summary(latest_run(project, "chapter_generation"))
                status.update(label="Chapter generated", state="complete")
            st.session_state.project = project
        if st.session_state.project:
            latest_chapter_run = latest_run(st.session_state.project, "chapter_generation")
            if latest_chapter_run:
                st.subheader("Latest Agent Run")
                render_run_summary(latest_chapter_run)

            plan_tab, draft_tab, review_tab, final_tab, trace_tab = st.tabs(["Plan", "Draft", "Review", "Final", "Trace"])
            with plan_tab:
                st.json(st.session_state.project.get("chapter_plans", [])[-1:] or {})
            with draft_tab:
                drafts = st.session_state.project.get("chapter_drafts", [])
                if drafts:
                    st.markdown(drafts[-1].get("markdown", ""))
                else:
                    st.info("No draft has been generated yet.")
            with review_tab:
                st.json(st.session_state.project.get("chapter_reviews", [])[-1:] or {})
            with final_tab:
                chapters = st.session_state.project.get("final_chapters", [])
                if chapters:
                    st.markdown(chapters[-1]["markdown"])
                else:
                    st.info("No final chapter has been generated yet.")
            with trace_tab:
                render_workflow_debug(st.session_state.project, st.session_state.project.get("book_structure", {}))

if page == "Export":
    if not st.session_state.project_id:
        st.info("Create a project first.")
    else:
        if st.button("Export Markdown", type="primary"):
            markdown = api_post(f"/projects/{st.session_state.project_id}/export/markdown")
            st.download_button("Download Markdown", markdown, file_name="book.md", mime="text/markdown")
