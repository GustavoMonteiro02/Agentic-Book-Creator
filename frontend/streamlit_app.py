from __future__ import annotations

import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
API_BASE_URL_FALLBACKS = os.getenv("API_BASE_URL_FALLBACKS", "")

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


def api_request(method: str, path: str, payload: dict | None = None):
    errors = []
    for base_url in api_base_urls():
        try:
            response = requests.request(method, f"{base_url}{path}", json=payload or None, timeout=30)
            response.raise_for_status()
            st.session_state.api_base_url = base_url
            return response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
        except requests.RequestException as exc:
            errors.append(f"{base_url}: {exc}")

    st.error("Could not connect to the FastAPI backend. If you are using Docker, start the full stack with `docker compose up --build`.")
    with st.expander("Connection attempts"):
        for error in errors:
            st.code(error)
    st.stop()


def api_post(path: str, payload: dict | None = None):
    return api_request("POST", path, payload)


def api_get(path: str):
    return api_request("GET", path)


if page == "Create Book":
    title = st.text_input("Book title", "Building Agentic AI Systems")
    idea = st.text_area(
        "Initial idea",
        "Quero criar um livro sobre agentes de inteligência artificial para developers de automação e RPA. Quero que seja prático, com exemplos, código, analogias e mini projetos.",
        height=180,
    )
    if st.button("Create project", type="primary"):
        project = api_post("/projects", {"title": title, "initial_idea": idea})
        st.session_state.project_id = project["project_id"]
        st.session_state.project = project
        st.success(f"Project created: {project['project_id']}")

if page == "Input Questions":
    if not st.session_state.project_id:
        st.info("Create a project first.")
    elif st.button("Generate adaptive questions", type="primary"):
        project = api_post(f"/projects/{st.session_state.project_id}/questions")
        st.session_state.project = project
        st.json(project.get("input_questions", []))

    if st.session_state.project and st.session_state.project.get("input_questions"):
        answers = []
        for question in st.session_state.project["input_questions"]:
            answer = st.text_input(question["question"], key=question["field"])
            if answer:
                answers.append({"field": question["field"], "answer": answer})
        if answers and st.button("Submit answers"):
            project = api_post(f"/projects/{st.session_state.project_id}/answers", {"answers": answers})
            st.session_state.project = project
            st.success("Brief, strategy, and structure generated.")

if page == "Book Brief":
    if st.session_state.project_id:
        st.json(api_post(f"/projects/{st.session_state.project_id}/requirements"))
    else:
        st.info("Create a project first.")

if page == "Book Strategy":
    if st.session_state.project_id:
        st.json(api_post(f"/projects/{st.session_state.project_id}/strategy"))
    else:
        st.info("Create a project first.")

if page == "Book Structure":
    if not st.session_state.project_id:
        st.info("Create a project first.")
    else:
        st.json(api_post(f"/projects/{st.session_state.project_id}/structure"))
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Approve structure", type="primary"):
                st.session_state.project = api_post(
                    f"/projects/{st.session_state.project_id}/approve-structure",
                    {"approved": True},
                )
                st.success("Structure approved.")
        with col2:
            revision = st.text_input("Revision request")
            if st.button("Request revision") and revision:
                st.session_state.project = api_post(
                    f"/projects/{st.session_state.project_id}/approve-structure",
                    {"approved": False, "revision_request": revision},
                )
                st.warning("Revision request saved.")

if page == "Chapter Workspace":
    if not st.session_state.project_id:
        st.info("Create a project first.")
    else:
        chapter_number = st.number_input("Chapter", min_value=1, value=1)
        if st.button("Generate chapter", type="primary"):
            project = api_post(f"/projects/{st.session_state.project_id}/chapters/{chapter_number}/generate")
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
