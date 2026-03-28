import random
from app.models.topic import Entry

def build_topic_test_questions(entries: list[Entry]) -> list[dict]:
    # ✅ shuffle entries so questions come randomly
    shuffled = entries.copy()
    random.shuffle(shuffled)

    total_questions = min(len(shuffled), 8)
    selected = shuffled[:total_questions]
    questions = []

    for index, entry in enumerate(selected):
        distractors = [e for e in shuffled if e.uid != entry.uid][index:index + 3]

        if len(distractors) < 3:
            extra = [
                e for e in shuffled
                if e.uid != entry.uid and e not in distractors
            ][:3 - len(distractors)]
            distractors.extend(extra)

        raw_options = [entry.uzbek] + [d.uzbek for d in distractors]
        # ✅ shuffle options too so correct answer isn't always first
        random.shuffle(raw_options)

        questions.append({
            "id": f"{entry.topic_uid}-{entry.uid}",
            "prompt": f"{entry.latin} so'zining ma'nosini toping",
            "correct_answer": entry.uzbek,
            "options": raw_options,
        })

    return questions


def build_final_test_questions(all_entries: list[Entry], total: int = 50) -> list[dict]:
    # ✅ random.sample already picks randomly, but shuffle the result too
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
        # ✅ shuffle options too
        random.shuffle(raw_options)

        questions.append({
            "id": f"final-{entry.uid}",
            "prompt": f"{entry.latin} so'zining ma'nosini toping",
            "correct_answer": entry.uzbek,
            "options": raw_options,
        })

    return questions
