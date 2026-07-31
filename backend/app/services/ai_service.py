"""
AI generation service.

Generates summaries, flashcards, and quizzes from a document's extracted
text. Uses Google Gemini when GEMINI_API_KEY is configured. If no key is
configured (or the call fails), falls back to a lightweight offline
generator so the feature still works end-to-end without external
dependencies.
"""

import json
import re

from app.core.config import settings

MAX_SOURCE_CHARS = 12000  # keep prompts small & cheap


def _clip(text: str) -> str:
    text = text.strip()
    if len(text) > MAX_SOURCE_CHARS:
        text = text[:MAX_SOURCE_CHARS]
    return text


def _extract_json(raw: str) -> dict | list:
    """
    Gemini sometimes wraps JSON in markdown fences or adds stray text.
    Pull out the first valid JSON object/array.
    """
    raw = raw.strip()
    raw = re.sub(r"^```(json)?", "", raw.strip(), flags=re.IGNORECASE).strip()
    raw = re.sub(r"```$", "", raw.strip()).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    match = re.search(r"(\{.*\}|\[.*\])", raw, flags=re.DOTALL)
    if match:
        return json.loads(match.group(1))

    raise ValueError("Could not parse JSON from AI response.")


def _gemini_available() -> bool:
    return bool(settings.GEMINI_API_KEY)


def _call_gemini(prompt: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(settings.AI_MODEL or "gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text


# --------------------------------------------------------------------------- #
# Summary
# --------------------------------------------------------------------------- #

def generate_summary(text: str) -> str:
    text = _clip(text)

    if _gemini_available():
        try:
            prompt = (
                "You are an expert study assistant. Summarize the following "
                "document for a student studying for an exam. Write clear, "
                "well-organized prose using short paragraphs and, where "
                "helpful, bullet points for key facts. Aim for 150-350 words. "
                "Do not include a title or preamble, just the summary itself.\n\n"
                f"DOCUMENT:\n{text}"
            )
            result = _call_gemini(prompt)
            if result and result.strip():
                return result.strip()
        except Exception:
            pass  # fall through to offline fallback

    return _offline_summary(text)


def _offline_summary(text: str) -> str:
    """
    Naive extractive summary: picks the most information-dense sentences.
    Used only when Gemini is unavailable or fails.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 25]

    if not sentences:
        return "This document does not contain enough extractable text to summarize."

    word_freq: dict[str, int] = {}
    for sentence in sentences:
        for word in re.findall(r"[a-zA-Z]{4,}", sentence.lower()):
            word_freq[word] = word_freq.get(word, 0) + 1

    def score(sentence: str) -> float:
        words = re.findall(r"[a-zA-Z]{4,}", sentence.lower())
        if not words:
            return 0
        return sum(word_freq.get(w, 0) for w in words) / len(words)

    ranked = sorted(sentences, key=score, reverse=True)
    top = ranked[: min(8, len(ranked))]
    # Restore original order for readability
    ordered = [s for s in sentences if s in top]

    return (
        "(Offline summary — configure GEMINI_API_KEY for AI-generated summaries)\n\n"
        + " ".join(ordered)
    )


# --------------------------------------------------------------------------- #
# Flashcards
# --------------------------------------------------------------------------- #

def generate_flashcards(text: str, count: int = 10) -> list[dict]:
    text = _clip(text)
    count = max(3, min(count, 25))

    if _gemini_available():
        try:
            prompt = (
                f"You are an expert study assistant. Read the document below and "
                f"create exactly {count} flashcards to help a student memorize "
                f"the key concepts. Each flashcard has a short question and a "
                f"concise answer.\n\n"
                'Respond with ONLY valid JSON: a list of objects like '
                '[{"question": "...", "answer": "..."}]. No markdown, no preamble.\n\n'
                f"DOCUMENT:\n{text}"
            )
            raw = _call_gemini(prompt)
            data = _extract_json(raw)

            cards = []
            for item in data:
                q = str(item.get("question", "")).strip()
                a = str(item.get("answer", "")).strip()
                if q and a:
                    cards.append({"question": q, "answer": a})

            if cards:
                return cards[:count]
        except Exception:
            pass  # fall through to offline fallback

    return _offline_flashcards(text, count)


def _offline_flashcards(text: str, count: int) -> list[dict]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s.strip() for s in sentences if 30 < len(s.strip()) < 300]

    cards = []
    for sentence in sentences:
        if len(cards) >= count:
            break
        words = sentence.split()
        if len(words) < 6:
            continue
        # Blank out a mid-sentence keyword to make a simple Q/A pair.
        candidates = [
            i for i, w in enumerate(words)
            if len(re.sub(r"[^a-zA-Z]", "", w)) > 5
        ]
        if not candidates:
            continue
        idx = candidates[len(candidates) // 2]
        answer = words[idx]
        question_words = words.copy()
        question_words[idx] = "____"
        question = "Fill in the blank: " + " ".join(question_words)
        cards.append({"question": question, "answer": re.sub(r"[^\w-]", "", answer)})

    if not cards:
        cards = [{
            "question": "What is this document about?",
            "answer": "Not enough extractable text to generate flashcards automatically.",
        }]

    return cards


# --------------------------------------------------------------------------- #
# Quiz
# --------------------------------------------------------------------------- #

def generate_quiz(text: str, count: int = 5) -> dict:
    text = _clip(text)
    count = max(3, min(count, 20))

    if _gemini_available():
        try:
            prompt = (
                f"You are an expert study assistant. Read the document below and "
                f"create a multiple-choice quiz with exactly {count} questions to "
                f"test understanding of the material. Each question has 4 options "
                f"(A, B, C, D) and exactly one correct answer.\n\n"
                'Respond with ONLY valid JSON in this exact shape:\n'
                '{"title": "Quiz title", "questions": [{"question": "...", '
                '"option_a": "...", "option_b": "...", "option_c": "...", '
                '"option_d": "...", "correct_answer": "A"}]}\n'
                "correct_answer must be one of \"A\", \"B\", \"C\", \"D\". "
                "No markdown, no preamble.\n\n"
                f"DOCUMENT:\n{text}"
            )
            raw = _call_gemini(prompt)
            data = _extract_json(raw)

            questions = []
            for item in data.get("questions", []):
                correct = str(item.get("correct_answer", "")).strip().upper()
                if correct not in ("A", "B", "C", "D"):
                    continue
                questions.append({
                    "question": str(item.get("question", "")).strip(),
                    "option_a": str(item.get("option_a", "")).strip(),
                    "option_b": str(item.get("option_b", "")).strip(),
                    "option_c": str(item.get("option_c", "")).strip(),
                    "option_d": str(item.get("option_d", "")).strip(),
                    "correct_answer": correct,
                })

            if questions:
                title = str(data.get("title") or "Generated Quiz").strip()
                return {"title": title, "questions": questions[:count]}
        except Exception:
            pass  # fall through to offline fallback

    return _offline_quiz(text, count)


def _offline_quiz(text: str, count: int) -> dict:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s.strip() for s in sentences if 30 < len(s.strip()) < 250]

    questions = []
    pool_words = list(set(re.findall(r"\b[A-Za-z]{5,}\b", text)))

    for sentence in sentences:
        if len(questions) >= count:
            break
        words = sentence.split()
        candidates = [
            i for i, w in enumerate(words)
            if len(re.sub(r"[^a-zA-Z]", "", w)) > 5
        ]
        if not candidates or len(pool_words) < 4:
            continue

        idx = candidates[len(candidates) // 2]
        correct_word = re.sub(r"[^\w-]", "", words[idx])
        if not correct_word:
            continue

        question_words = words.copy()
        question_words[idx] = "____"
        question_text = " ".join(question_words)

        distractors = [w for w in pool_words if w.lower() != correct_word.lower()]
        if len(distractors) < 3:
            continue
        import random
        random.shuffle(distractors)
        options = [correct_word] + distractors[:3]
        random.shuffle(options)
        correct_letter = "ABCD"[options.index(correct_word)]

        questions.append({
            "question": question_text,
            "option_a": options[0],
            "option_b": options[1],
            "option_c": options[2],
            "option_d": options[3],
            "correct_answer": correct_letter,
        })

    if not questions:
        questions = [{
            "question": "Not enough extractable text to generate a quiz automatically.",
            "option_a": "N/A",
            "option_b": "N/A",
            "option_c": "N/A",
            "option_d": "N/A",
            "correct_answer": "A",
        }]

    return {"title": "Offline Generated Quiz", "questions": questions}


# --------------------------------------------------------------------------- #
# Daily Mentor Briefing
# --------------------------------------------------------------------------- #

def generate_daily_mentor_briefing(user_name: str, context: dict) -> dict:
    """
    Acts as a personal study mentor: reviews the student's tasks,
    assignments, deadlines, and today's study activity, then returns a
    structured daily briefing — a greeting, motivational note, prioritized
    action list, a suggested time-blocked schedule, and study tips.
    """
    if _gemini_available():
        try:
            prompt = _mentor_prompt(user_name, context)
            raw = _call_gemini(prompt)
            data = _extract_json(raw)
            briefing = _normalize_mentor_briefing(data)
            if briefing:
                return briefing
        except Exception:
            pass  # fall through to offline fallback

    return _offline_mentor_briefing(user_name, context)


def _mentor_prompt(user_name: str, context: dict) -> str:
    return (
        "You are an encouraging, practical personal study mentor for a "
        f"student named {user_name}. Using the JSON data below about their "
        "tasks, assignments, deadlines, and today's study activity, write a "
        "short daily briefing. Be warm but concise, like a mentor who knows "
        "their real workload and wants them to succeed without burning out.\n\n"
        f"STUDENT DATA (JSON):\n{json.dumps(context)}\n\n"
        "Respond with ONLY valid JSON in this exact shape:\n"
        '{"greeting": "one warm sentence addressing them by name", '
        '"motivation": "1-2 sentence encouraging note grounded in their actual workload", '
        '"priorities": [{"title": "...", "why": "short reason", "urgency": "high|medium|low"}], '
        '"schedule": [{"time": "e.g. 9:00 AM - 10:00 AM", "activity": "..."}], '
        '"tips": ["short actionable tip", "..."]}\n'
        "Base priorities and the schedule on the real assignments/deadlines/"
        "tasks given — if nothing is due, say so honestly and suggest a "
        "light, sustainable plan instead of inventing urgency. Keep the "
        "schedule realistic (4-6 blocks) and include breaks. No markdown, "
        "no preamble, JSON only."
    )


def _normalize_mentor_briefing(data: dict) -> dict | None:
    if not isinstance(data, dict):
        return None

    greeting = str(data.get("greeting", "")).strip()
    motivation = str(data.get("motivation", "")).strip()

    priorities = []
    for item in data.get("priorities", []) or []:
        title = str(item.get("title", "")).strip()
        if not title:
            continue
        urgency = str(item.get("urgency", "medium")).strip().lower()
        if urgency not in ("high", "medium", "low"):
            urgency = "medium"
        priorities.append({
            "title": title,
            "why": str(item.get("why", "")).strip(),
            "urgency": urgency,
        })

    schedule = []
    for block in data.get("schedule", []) or []:
        time_label = str(block.get("time", "")).strip()
        activity = str(block.get("activity", "")).strip()
        if time_label and activity:
            schedule.append({"time": time_label, "activity": activity})

    tips = [str(t).strip() for t in (data.get("tips") or []) if str(t).strip()]

    if not greeting or not motivation:
        return None

    return {
        "greeting": greeting,
        "motivation": motivation,
        "priorities": priorities,
        "schedule": schedule,
        "tips": tips,
    }


def _offline_mentor_briefing(user_name: str, context: dict) -> dict:
    """Deterministic fallback used when Gemini is unavailable or fails."""
    tasks = context.get("tasks", [])
    assignments = context.get("assignments", [])
    deadlines = context.get("deadlines", [])
    minutes_studied = context.get("minutes_studied_today", 0)

    open_tasks = [t for t in tasks if not t.get("completed")]

    priorities = []
    for a in assignments[:3]:
        priorities.append({
            "title": a.get("title", "Assignment"),
            "why": f"Due {a.get('due_date') or 'soon'}.",
            "urgency": "high" if a.get("priority") == "high" else "medium",
        })
    for d in deadlines[:3]:
        if len(priorities) >= 5:
            break
        priorities.append({
            "title": d.get("title", "Deadline"),
            "why": f"{d.get('type') or 'Deadline'} on {d.get('date') or 'an upcoming date'}.",
            "urgency": "medium",
        })
    for t in open_tasks[:5]:
        if len(priorities) >= 6:
            break
        priorities.append({
            "title": t.get("title", "Task"),
            "why": "On today's planner.",
            "urgency": "low",
        })

    if priorities:
        schedule = [
            {"time": "9:00 AM - 10:30 AM", "activity": priorities[0]["title"]},
            {"time": "10:30 AM - 10:45 AM", "activity": "Short break"},
            {
                "time": "10:45 AM - 12:00 PM",
                "activity": priorities[1]["title"] if len(priorities) > 1 else "Review notes",
            },
            {
                "time": "1:00 PM - 2:30 PM",
                "activity": priorities[2]["title"] if len(priorities) > 2 else "Deep work session",
            },
            {"time": "2:30 PM - 2:45 PM", "activity": "Short break"},
            {"time": "2:45 PM - 4:00 PM", "activity": "Wrap up & review tomorrow's plan"},
        ]
        motivation = (
            f"You've got {len(priorities)} thing{'s' if len(priorities) != 1 else ''} "
            "worth focusing on today — tackle the biggest one first while your energy is high."
        )
    else:
        schedule = [
            {"time": "Anytime today", "activity": "Light review of recent material"},
            {"time": "Anytime today", "activity": "Get ahead by skimming next week's topics"},
        ]
        motivation = "Nothing urgent is due — a good day to get ahead or rest and recharge."

    first_name = user_name.split(" ")[0] if user_name else "there"

    return {
        "greeting": f"Hey {first_name}, here's your day.",
        "motivation": motivation,
        "priorities": priorities,
        "schedule": schedule,
        "tips": [
            "Study in focused blocks with short breaks (try 45-50 min on, 10 min off).",
            f"You've logged {minutes_studied} minute{'s' if minutes_studied != 1 else ''} "
            "of study today — every bit counts.",
        ],
    }
