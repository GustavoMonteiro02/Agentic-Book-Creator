.PHONY: api ui test

api:
	uvicorn app.api.main:app --reload

ui:
	streamlit run frontend/streamlit_app.py

test:
	pytest -q

migrate:
	alembic upgrade head
