from app.database.repositories import project_repository


class ProjectService:
    def create_project(self, title: str, initial_idea: str):
        return project_repository.create(title=title, initial_idea=initial_idea)

    def list_projects(self):
        return project_repository.list()

    def get_project(self, project_id: str):
        return project_repository.get(project_id)


project_service = ProjectService()
