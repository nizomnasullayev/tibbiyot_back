import json
import re
from typing import Any

import httpx
from fastapi import HTTPException, status
from pydantic import ValidationError

from app.core.config import settings
from app.schema.baamboozle_question_schema import (
    ALLOWED_CATEGORIES,
    BaamboozleAIGenerateRequest,
    BaamboozleQuestionCreate,
)


def _choose_category(index: int, categories: list[int] | None) -> int:
    ordered_categories = sorted(categories or ALLOWED_CATEGORIES)
    return ordered_categories[index % len(ordered_categories)]


def _build_prompt(data: BaamboozleAIGenerateRequest) -> str:
    category_line = (
        f"Use only these categories: {data.categories}"
        if data.categories
        else "Use categories from this allowed set: [50,100,150,200,250,300,350,400,450,500]"
    )
    difficulty_line = data.difficulty_notes or "Balance difficulty naturally for the class level."
    language_line = "Write all questions and answers in Uzbek language." if data.language == "uz" else "Write all questions and answers in English."
    return (
        "Generate Baamboozle game questions as JSON.\n"
        f"Subject: {data.subject}\n"
        f"Teacher notes: {data.topic_description}\n"
        f"Difficulty notes: {difficulty_line}\n"
        f"{language_line}\n"
        f"Need exactly {data.number_of_questions} questions.\n"
        f"{category_line}\n"
        "Return ONLY valid JSON object in this format:\n"
        '{"questions":[{"category":100,"question":"...","answer":"..."}]}\n'
        "Constraints:\n"
        "- Make each question unique; do not repeat sentence patterns.\n"
        "- Avoid placeholders, meta text, and template wording.\n"
        "- Answers must be specific, correct, and concise.\n"
        "- Keep content classroom-safe.\n"
    )


def _clean_possible_json(raw: str) -> str:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

    if text.startswith("{") and text.endswith("}"):
        return text

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


def _extract_topic_points(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []
    parts = [part.strip(" ,") for part in re.split(r"[.;\n,]+", normalized) if part.strip()]
    return parts or [normalized]


def _resolve_gemini_model(api_key: str, preferred_model: str) -> str:
    preferred = (preferred_model or "").strip()
    if preferred.startswith("models/"):
        preferred = preferred.split("/", 1)[1]

    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(list_url)
        response.raise_for_status()
        models = (response.json() or {}).get("models") or []
    except Exception:
        return preferred or "gemini-2.0-flash"

    supported: list[str] = []
    for model in models:
        if not isinstance(model, dict):
            continue
        name = str(model.get("name", "")).strip()  # e.g., models/gemini-2.0-flash
        methods = model.get("supportedGenerationMethods") or []
        if "generateContent" not in methods:
            continue
        if name.startswith("models/"):
            name = name.split("/", 1)[1]
        if name:
            supported.append(name)

    if not supported:
        return preferred or "gemini-2.0-flash"
    if preferred and preferred in supported:
        return preferred
    return supported[0]


def _generate_local_fallback(data: BaamboozleAIGenerateRequest) -> list[BaamboozleQuestionCreate]:
    points = _extract_topic_points(data.topic_description)
    if not points:
        points = [data.subject]

    if data.language == "uz":
        templates = [
            ("{topic} nima?", "{topic} {subject} fanidagi asosiy tushunchalardan biri."),
            ("Nega {topic} {subject} fanida muhim?", "{topic} {subject}dagi asosiy g'oyalarni tushuntiradi."),
            ("{topic}ga bitta real misol keltiring.", "{topic}ga oid darsda ko'rilgan istalgan to'g'ri misol."),
            ("{topic} haqida bitta muhim faktni ayting.", "{topic} bo'yicha darsda o'rgatilgan to'g'ri fakt."),
            ("{topic}ni sinfdoshingizga qanday tushuntirasiz?", "{topic}ni sodda va aniq tarzda tushuntirish."),
            ("{topic} bo'yicha o'quvchilar ko'p qiladigan xatolik nima?", "Keng tarqalgan xato va uning to'g'ri talqini."),
            ("{topic} bilan eng bog'liq kalit so'zni ayting.", "{topic} bilan birga o'rganilgan asosiy atama."),
            ("{topic} dars maqsadi bilan qanday bog'langan?", "U dars maqsadini asosiy tushunchani mustahkamlash orqali qo'llab-quvvatlaydi."),
        ]
    else:
        templates = [
            ("What is {topic}?", "{topic} is a core concept in {subject}."),
            ("Why is {topic} important in {subject}?", "{topic} is important because it explains key ideas in {subject}."),
            ("Give one real example of {topic}.", "Any valid classroom example related to {topic}."),
            ("Name one key fact about {topic}.", "One correct fact taught in class about {topic}."),
            ("How would you explain {topic} to a classmate?", "A short, clear explanation of {topic} in simple words."),
            ("What is one common mistake students make about {topic}?", "A typical misconception and its correction."),
            ("Which keyword is most connected to {topic}?", "A core keyword taught together with {topic}."),
            ("How does {topic} connect to the lesson objective?", "It supports the lesson objective by reinforcing the main concept."),
        ]

    created: list[BaamboozleQuestionCreate] = []
    for index in range(data.number_of_questions):
        lesson_point = points[index % len(points)]
        q_template, a_template = templates[index % len(templates)]
        category = _choose_category(index, data.categories)
        question = q_template.format(topic=lesson_point, subject=data.subject)
        answer = a_template.format(topic=lesson_point, subject=data.subject)
        created.append(
            BaamboozleQuestionCreate(
                category=category,
                question=question,
                answer=answer,
            )
        )

    return created


def _extract_question_payloads(raw_content: str, data: BaamboozleAIGenerateRequest) -> list[dict[str, Any]]:
    try:
        parsed = json.loads(_clean_possible_json(raw_content))
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI returned invalid JSON: {exc.msg}",
        ) from exc

    questions = parsed.get("questions")
    if not isinstance(questions, list):
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI response missing questions list")

    if not questions:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI returned empty questions list")

    payloads: list[dict[str, Any]] = []
    for index, item in enumerate(questions[: data.number_of_questions]):
        if not isinstance(item, dict):
            continue

        question_text = str(item.get("question", "")).strip()
        answer_text = str(item.get("answer", "")).strip()

        ai_category = item.get("category")
        valid_category = (
            int(ai_category)
            if isinstance(ai_category, int) and ai_category in ALLOWED_CATEGORIES
            else _choose_category(index, data.categories)
        )

        if not question_text or not answer_text:
            continue

        payloads.append(
            {
                "category": valid_category,
                "question": question_text,
                "answer": answer_text,
            }
        )

    if not payloads:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI returned no usable questions",
        )

    return payloads


def _generate_with_openai_compatible(data: BaamboozleAIGenerateRequest) -> list[BaamboozleQuestionCreate]:
    api_key = (settings.OPENAI_API_KEY or "").strip()
    if not api_key or api_key.lower() in {"your_key_here", "changeme", "placeholder"}:
        return _generate_local_fallback(data)

    prompt = _build_prompt(data)
    base_url = settings.OPENAI_BASE_URL.rstrip("/")

    request_body = {
        "model": settings.OPENAI_MODEL,
        "temperature": 0.5,
        "messages": [
            {
                "role": "system",
                "content": "You are an assistant that creates clear classroom game questions.",
            },
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
    }

    try:
        with httpx.Client(timeout=60) as client:
            response = client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=request_body,
            )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        if settings.AI_ALLOW_FALLBACK:
            return _generate_local_fallback(data)
        detail = f"AI provider error: {exc.response.status_code}"
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail) from exc
    except httpx.HTTPError as exc:
        if settings.AI_ALLOW_FALLBACK:
            return _generate_local_fallback(data)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to reach AI provider",
        ) from exc

    try:
        content = response.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        if settings.AI_ALLOW_FALLBACK:
            return _generate_local_fallback(data)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unexpected AI response format",
        ) from exc
    try:
        payloads = _extract_question_payloads(content, data)
    except HTTPException:
        if settings.AI_ALLOW_FALLBACK:
            return _generate_local_fallback(data)
        raise

    validated: list[BaamboozleQuestionCreate] = []
    for payload in payloads:
        try:
            validated.append(BaamboozleQuestionCreate(**payload))
        except ValidationError:
            continue

    if not validated:
        if settings.AI_ALLOW_FALLBACK:
            return _generate_local_fallback(data)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI generated questions failed validation",
        )

    return validated


def _generate_with_gemini(data: BaamboozleAIGenerateRequest) -> list[BaamboozleQuestionCreate]:
    api_key = (settings.GEMINI_API_KEY or "").strip()
    if not api_key or api_key.lower() in {"your_key_here", "changeme", "placeholder"}:
        return _generate_local_fallback(data)

    prompt = _build_prompt(data)
    model = _resolve_gemini_model(api_key, settings.GEMINI_MODEL)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    request_body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.5,
            "responseMimeType": "application/json",
        },
    }

    try:
        with httpx.Client(timeout=60) as client:
            response = client.post(url, json=request_body)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        if settings.AI_ALLOW_FALLBACK:
            return _generate_local_fallback(data)
        body_text = (exc.response.text or "")[:300]
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gemini provider error: {exc.response.status_code}. {body_text}",
        ) from exc
    except httpx.HTTPError as exc:
        if settings.AI_ALLOW_FALLBACK:
            return _generate_local_fallback(data)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to reach Gemini provider",
        ) from exc

    try:
        body = response.json()
        candidates = body.get("candidates") or []
        parts = []
        for candidate in candidates:
            candidate_parts = (candidate.get("content") or {}).get("parts") or []
            parts.extend(candidate_parts)
        text_chunks = [part.get("text", "") for part in parts if isinstance(part, dict)]
        content = "\n".join(chunk for chunk in text_chunks if chunk).strip()
        if not content:
            if settings.AI_ALLOW_FALLBACK:
                return _generate_local_fallback(data)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Gemini returned empty content")
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        if settings.AI_ALLOW_FALLBACK:
            return _generate_local_fallback(data)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Unexpected Gemini response format") from exc

    try:
        payloads = _extract_question_payloads(content, data)
    except HTTPException:
        if settings.AI_ALLOW_FALLBACK:
            return _generate_local_fallback(data)
        raise
    validated: list[BaamboozleQuestionCreate] = []
    for payload in payloads:
        try:
            validated.append(BaamboozleQuestionCreate(**payload))
        except ValidationError:
            continue

    if not validated:
        if settings.AI_ALLOW_FALLBACK:
            return _generate_local_fallback(data)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Gemini generated questions failed validation",
        )
    return validated


def generate_question_creates(data: BaamboozleAIGenerateRequest) -> list[BaamboozleQuestionCreate]:
    provider = (settings.AI_PROVIDER or "openai").strip().lower()
    if provider == "gemini":
        return _generate_with_gemini(data)
    return _generate_with_openai_compatible(data)
