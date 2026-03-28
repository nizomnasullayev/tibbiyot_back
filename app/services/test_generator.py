import random
from app.models.topic import Entry

def build_topic_test_questions(entries: list[Entry]) -> list[dict]:
    total_questions = min(len(entries), 8)
    selected = entries[:total_questions]
    questions = []

    for index, entry in enumerate(selected):
        distractors = [e for e in entries if e.uid != entry.uid][index:index + 3]

        if len(distractors) < 3:
            extra = [
                e for e in entries
                if e.uid != entry.uid and e not in distractors
            ][:3 - len(distractors)]
            distractors.extend(extra)

        raw_options = [entry.uzbek] + [d.uzbek for d in distractors]
        shift = index % len(raw_options)
        options = [raw_options[(i + shift) % len(raw_options)] for i in range(len(raw_options))]

        questions.append({
            "id": f"{entry.topic_uid}-{entry.uid}",
            "prompt": f"{entry.latin} so'zining ma'nosini toping",
            "correct_answer": entry.uzbek,
            "options": options,
        })

    return questions


def build_final_test_questions(all_entries: list[Entry], total: int = 50) -> list[dict]:
    # Randomly pick 50 entries from all topics
    selected = random.sample(all_entries, min(len(all_entries), total))
    questions = []

    for index, entry in enumerate(selected):
        distractors = [e for e in all_entries if e.uid != entry.uid][index:index + 3]

        if len(distractors) < 3:
            extra = [
                e for e in all_entries
                if e.uid != entry.uid and e not in distractors
            ][:3 - len(distractors)]
            distractors.extend(extra)

        raw_options = [entry.uzbek] + [d.uzbek for d in distractors]
        shift = index % len(raw_options)
        options = [raw_options[(i + shift) % len(raw_options)] for i in range(len(raw_options))]

        questions.append({
            "id": f"final-{entry.uid}",
            "prompt": f"{entry.latin} so'zining ma'nosini toping",
            "correct_answer": entry.uzbek,
            "options": options,
        })

    return questions