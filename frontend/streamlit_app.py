from __future__ import annotations

import os

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
CHAPTER_AGENT_STEPS = [
    ("Chapter Planner Agent", "Selects the chapter objective, key concepts, examples, and exercises."),
    ("Chapter Writer Agent", "Drafts the chapter from the approved structure and project memory."),
    ("Technical Reviewer Agent", "Checks technical accuracy, gaps, and implementation clarity."),
    ("Editor Agent", "Rewrites the draft into the final chapter markdown."),
    ("Checkpoint Service", "Stores the final chapter and run metadata."),
]

st.set_page_config(page_title="Agentic Book Creator", layout="wide")
st.title("Agentic Book Creator")

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


def refresh_project():
    if st.session_state.project_id:
        st.session_state.project = api_get(f"/projects/{st.session_state.project_id}")


def render_agent_activity(steps: list[tuple[str, str]]):
    for index, (agent_name, work) in enumerate(steps, start=1):
        st.write(f"{index}. **{agent_name}**")
        st.caption(work)


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


def render_project_progress():
    project = st.session_state.project
    if not project:
        return

    st.sidebar.divider()
    st.sidebar.caption("Current project")
    st.sidebar.code(project.get("project_id", st.session_state.project_id), language="text")
    st.sidebar.progress(workflow_progress(project))
    for step in workflow_steps(project):
        marker = "[x]" if step["complete"] else "[ ]"
        st.sidebar.write(f"{marker} {step['label']}")
    st.sidebar.info(next_action(project))
    render_latest_runs(project)
    if st.sidebar.button("Refresh project"):
        refresh_project()
        st.rerun()


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
        if not st.session_state.project:
            refresh_project()
        if not st.session_state.project.get("input_questions"):
            if st.button("Generate adaptive questions", type="primary"):
                with st.status("Generating adaptive questions with Gemini...", expanded=True) as status:
                    render_agent_activity(QUESTION_AGENT_STEPS)
                    project = api_post(
                        f"/projects/{st.session_state.project_id}/questions",
                        timeout_seconds=LLM_REQUEST_TIMEOUT_SECONDS,
                    )
                    status.update(label="Questions generated", state="complete")
                st.session_state.project = project
                st.rerun()

    if st.session_state.project and st.session_state.project.get("input_questions"):
        st.info(next_action(st.session_state.project))
        answers = []
        for question in st.session_state.project["input_questions"]:
            answer = st.text_input(question["question"], key=question["field"])
            if answer:
                answers.append({"field": question["field"], "answer": answer})
        if answers and st.button("Submit answers"):
            with st.status("Building book brief, strategy, and structure...", expanded=True) as status:
                render_agent_activity(BOOK_PLAN_AGENT_STEPS)
                project = api_post(
                    f"/projects/{st.session_state.project_id}/answers",
                    {"answers": answers},
                    timeout_seconds=LLM_REQUEST_TIMEOUT_SECONDS,
                )
                status.update(label="Book plan generated", state="complete")
            st.session_state.project = project
            st.success("Brief, strategy, and structure generated.")
            st.info(next_action(project))

if page == "Book Brief":
    if st.session_state.project_id:
        project = api_post(
            f"/projects/{st.session_state.project_id}/requirements",
            timeout_seconds=LLM_REQUEST_TIMEOUT_SECONDS,
        )
        st.session_state.project = project
        st.json(project.get("book_requirements", project))
    else:
        st.info("Create a project first.")

if page == "Book Strategy":
    if st.session_state.project_id:
        project = api_post(
            f"/projects/{st.session_state.project_id}/strategy",
            timeout_seconds=LLM_REQUEST_TIMEOUT_SECONDS,
        )
        st.session_state.project = project
        st.json(project.get("book_strategy", project))
    else:
        st.info("Create a project first.")

if page == "Book Structure":
    if not st.session_state.project_id:
        st.info("Create a project first.")
    else:
        project = api_post(
            f"/projects/{st.session_state.project_id}/structure",
            timeout_seconds=LLM_REQUEST_TIMEOUT_SECONDS,
        )
        st.session_state.project = project
        st.json(project.get("book_structure", project))
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Approve structure", type="primary"):
                st.session_state.project = api_post(
                    f"/projects/{st.session_state.project_id}/approve-structure",
                    {"approved": True},
                )
                st.success("Structure approved.")
                st.rerun()
        with col2:
            revision = st.text_input("Revision request")
            if st.button("Request revision") and revision:
                st.session_state.project = api_post(
                    f"/projects/{st.session_state.project_id}/approve-structure",
                    {"approved": False, "revision_request": revision},
                )
                st.warning("Revision request saved.")
                st.rerun()

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
                status.update(label="Chapter generated", state="complete")
            st.session_state.project = project
        if st.session_state.project:
            st.subheader("Plan")
            st.json(st.session_state.project.get("chapter_plans", [])[-1:] or {})
            st.subheader("Technical Review")
            st.json(st.session_state.project.get("chapter_reviews", [])[-1:] or {})
            st.subheader("Final Chapter")
            chapters = st.session_state.project.get("final_chapters", [])
            if chapters:
                st.markdown(chapters[-1]["markdown"])

if page == "Export":
    if not st.session_state.project_id:
        st.info("Create a project first.")
    else:
        if st.button("Export Markdown", type="primary"):
            markdown = api_post(f"/projects/{st.session_state.project_id}/export/markdown")
            st.download_button("Download Markdown", markdown, file_name="book.md", mime="text/markdown")
