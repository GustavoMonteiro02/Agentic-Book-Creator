from app.agents.state import BookState
from app.llm.client import llm_client
from app.prompts.input_gathering_prompt import INPUT_GATHERING_PROMPT


QUESTION_BANK = {
    "book_goal": "Qual é o objetivo principal do livro para o leitor?",
    "target_audience": "Quem é o público-alvo principal?",
    "reader_level": "Qual é o nível técnico esperado do leitor?",
    "tone": "Que tom queres: prático, académico, conversacional ou executivo?",
    "preferred_structure": "Preferes uma estrutura do básico ao avançado, por projetos ou por problemas/soluções?",
    "chapter_format": "Cada capítulo deve incluir teoria, código, analogias, exercícios ou mini projetos?",
    "required_topics": "Há tecnologias ou temas obrigatórios a incluir?",
    "topics_to_avoid": "Há temas, claims ou estilos que devem ser evitados?",
    "output_formats": "Qual deve ser o formato final: Markdown, PDF, DOCX ou JSON?",
}


def gather_input(state: BookState) -> BookState:
    idea = state.get("initial_user_idea", "").lower()
    answers = " ".join(str(answer.get("answer", "")) for answer in state.get("user_answers", [])).lower()
    combined = f"{idea} {answers}"

    known_information = {
        "topic": state.get("initial_user_idea", "").strip(),
    }
    missing = []

    checks = {
        "target_audience": ["público", "publico", "developers", "rpa", "leitor", "audience"],
        "tone": ["tom", "prático", "pratico", "académico", "academico", "conversacional"],
        "reader_level": ["básico", "basico", "intermédio", "intermedio", "avançado", "avancado", "nível", "nivel"],
        "preferred_structure": ["estrutura", "projetos", "problemas", "soluções", "solucoes"],
        "chapter_format": ["capítulo", "capitulo", "exercícios", "exercicios", "mini projetos", "código", "codigo"],
        "output_formats": ["markdown", "pdf", "docx", "json"],
    }

    for field, keywords in checks.items():
        if any(keyword in combined for keyword in keywords):
            known_information[field] = "inferred_from_user_input"
        else:
            missing.append(field)

    follow_up_questions = [
        {"field": field, "question": QUESTION_BANK[field], "purpose": f"Clarify {field}"}
        for field in missing[:4]
    ]

    fallback = {
        **state,
        "missing_information": missing,
        "input_questions": follow_up_questions,
        "status": "awaiting_input" if follow_up_questions else "input_complete",
    }

    llm_result = llm_client.generate_json(
        system_prompt=INPUT_GATHERING_PROMPT,
        user_payload={
            "initial_user_idea": state.get("initial_user_idea", ""),
            "user_answers": state.get("user_answers", []),
            "known_information": known_information,
            "fallback_question_bank": QUESTION_BANK,
        },
        fallback={
            "missing_information": missing,
            "follow_up_questions": follow_up_questions,
            "known_information": known_information,
        },
    )

    input_questions = llm_result.get("follow_up_questions", follow_up_questions)
    missing_information = llm_result.get("missing_information", missing)

    return {
        **fallback,
        "missing_information": missing_information,
        "input_questions": input_questions,
        "status": "awaiting_input" if input_questions else "input_complete",
    }
