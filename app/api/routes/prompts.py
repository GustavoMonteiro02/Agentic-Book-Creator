from fastapi import APIRouter, HTTPException

from app.prompts.registry import get_prompt, list_prompts

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.get("")
def list_prompt_registry(include_templates: bool = False):
    return list_prompts(include_templates=include_templates)


@router.get("/{prompt_name}")
def get_prompt_definition(prompt_name: str, include_template: bool = True):
    try:
        return get_prompt(prompt_name, include_template=include_template)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Prompt not found") from exc
