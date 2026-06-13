import os


os.environ["DATABASE_URL"] = "sqlite:///./test_agentic_book_creator.db"
os.environ["LLM_ENABLED"] = "false"
os.environ["GEMINI_API_KEY"] = ""
os.environ["GOOGLE_API_KEY"] = ""
os.environ["OPENAI_API_KEY"] = ""
