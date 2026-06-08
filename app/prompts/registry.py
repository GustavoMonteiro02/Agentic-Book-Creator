from dataclasses import dataclass

from app.prompts.book_strategy_prompt import BOOK_STRATEGY_PROMPT
from app.prompts.chapter_planner_prompt import CHAPTER_PLANNER_PROMPT
from app.prompts.chapter_writer_prompt import CHAPTER_WRITER_PROMPT
from app.prompts.editor_prompt import EDITOR_PROMPT
from app.prompts.input_gathering_prompt import INPUT_GATHERING_PROMPT
from app.prompts.input_understanding_prompt import INPUT_UNDERSTANDING_PROMPT
from app.prompts.structure_designer_prompt import STRUCTURE_DESIGNER_PROMPT
from app.prompts.technical_review_prompt import TECHNICAL_REVIEW_PROMPT


@dataclass(frozen=True)
class PromptDefinition:
    name: str
    version: str
    description: str
    output_contract: str
    model_route: str
    template: str
    changelog: str


PROMPT_REGISTRY = {
    "input_gathering": PromptDefinition(
        name="input_gathering",
        version="mvp-v1",
        description="Identify known and missing information from a book idea.",
        output_contract="known_information, missing_information, follow_up_questions",
        model_route="small_llm",
        template=INPUT_GATHERING_PROMPT,
        changelog="Initial structured clarification prompt.",
    ),
    "input_understanding": PromptDefinition(
        name="input_understanding",
        version="mvp-v1",
        description="Convert user input into structured book requirements.",
        output_contract="BookRequirements",
        model_route="small_llm",
        template=INPUT_UNDERSTANDING_PROMPT,
        changelog="Initial requirements extraction prompt.",
    ),
    "book_strategy": PromptDefinition(
        name="book_strategy",
        version="mvp-v1",
        description="Create an editorial strategy for the book.",
        output_contract="BookStrategy",
        model_route="strong_llm",
        template=BOOK_STRATEGY_PROMPT,
        changelog="Initial strategy prompt.",
    ),
    "structure_designer": PromptDefinition(
        name="structure_designer",
        version="mvp-v1",
        description="Design editable parts, chapters, sections, examples, and exercises.",
        output_contract="BookStructure",
        model_route="strong_llm",
        template=STRUCTURE_DESIGNER_PROMPT,
        changelog="Initial structure prompt.",
    ),
    "chapter_planner": PromptDefinition(
        name="chapter_planner",
        version="mvp-v1",
        description="Plan a chapter before drafting.",
        output_contract="ChapterPlan",
        model_route="strong_llm",
        template=CHAPTER_PLANNER_PROMPT,
        changelog="Initial chapter planning prompt.",
    ),
    "chapter_writer": PromptDefinition(
        name="chapter_writer",
        version="mvp-v1",
        description="Draft a chapter from an approved chapter plan.",
        output_contract="ChapterDraftMarkdown",
        model_route="strong_llm",
        template=CHAPTER_WRITER_PROMPT,
        changelog="Initial long-form chapter writing prompt.",
    ),
    "technical_review": PromptDefinition(
        name="technical_review",
        version="mvp-v1",
        description="Review a chapter for technical quality and correctness.",
        output_contract="TechnicalReview",
        model_route="strong_llm",
        template=TECHNICAL_REVIEW_PROMPT,
        changelog="Initial technical review prompt.",
    ),
    "editor": PromptDefinition(
        name="editor",
        version="mvp-v1",
        description="Improve style and readability while preserving technical meaning.",
        output_contract="EditedChapterMarkdown",
        model_route="small_llm",
        template=EDITOR_PROMPT,
        changelog="Initial editorial polishing prompt.",
    ),
}


def list_prompts(include_templates: bool = False) -> list[dict]:
    return [_serialize_prompt(prompt, include_template=include_templates) for prompt in PROMPT_REGISTRY.values()]


def get_prompt(name: str, include_template: bool = True) -> dict:
    prompt = PROMPT_REGISTRY[name]
    return _serialize_prompt(prompt, include_template=include_template)


def _serialize_prompt(prompt: PromptDefinition, include_template: bool) -> dict:
    data = {
        "name": prompt.name,
        "version": prompt.version,
        "description": prompt.description,
        "output_contract": prompt.output_contract,
        "model_route": prompt.model_route,
        "changelog": prompt.changelog,
    }
    if include_template:
        data["template"] = prompt.template
    return data
