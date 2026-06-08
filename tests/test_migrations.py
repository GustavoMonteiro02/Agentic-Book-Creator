from pathlib import Path


def test_initial_migration_defines_core_tables():
    migration = Path("alembic/versions/0001_initial_schema.py")

    content = migration.read_text()

    assert 'revision = "0001_initial_schema"' in content
    for table_name in [
        "book_projects",
        "user_inputs",
        "input_questions",
        "book_requirements",
        "book_strategies",
        "book_structures",
        "book_chapters",
        "chapter_reviews",
        "execution_runs",
    ]:
        assert f'"{table_name}"' in content


def test_alembic_env_uses_application_database_url():
    env = Path("alembic/env.py").read_text()

    assert "get_settings" in env
    assert "settings.database_url" in env
    assert "target_metadata = Base.metadata" in env
