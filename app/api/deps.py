from app.services.book_service import book_service
from app.services.chapter_service import chapter_service
from app.services.export_service import export_service
from app.services.project_service import project_service


def get_project_service():
    return project_service


def get_book_service():
    return book_service


def get_chapter_service():
    return chapter_service


def get_export_service():
    return export_service
