import random
from typing import List, Dict, Optional
from database import Database

db = Database()

class AdaptiveEngine:
    """
    Advanced Adaptive AI Engine (Behavioral & Smart Predictive Model)
    """

    def get_next_question(self, session: dict) -> Optional[dict]:
        """
        Picks next question using Performance Window and Ability Score.
        """
        difficulty = session["current_difficulty"]
        topics = session["topics"]
        categories = session.get("categories", [])
        language = session.get("language")
        answered_ids = [r["question_id"] for r in session["responses"]]

        # Trend Analysis (Last 5 questions)
        if len(session["responses"]) >= 3:
            last_n = session["responses"][-3:]
            acc = float(sum(1 for r in last_n if r["is_correct"])) / len(last_n)
            avg_times = [float(r["response_time"]) for r in last_n]
            avg_time = sum(avg_times) / len(avg_times)
            
            # Jump logic: Fast and Accurate
            if acc == 1.0 and avg_time < 15:
                difficulty = int(min(5, difficulty + 2))
            elif acc < 0.33:
                difficulty = int(max(1, difficulty - 1))

        # Shuffle topics to avoid boredom if multiple selected
        random.shuffle(topics)
        
        diff_sequence = [difficulty, difficulty - 1, difficulty + 1, difficulty - 2, difficulty + 2]
        for d_val in diff_sequence:
            d_val = int(max(1, min(5, d_val)))
            questions = db.get_questions_by_filter(topics, d_val, exclude_ids=answered_ids, language=language, categories=categories)
            if questions:
                return self._package_question(random.choice(questions), d_val)

        # Final Fallback: Search across ALL subjects if selected ones are exhausted
        all_topics = db.get_all_topics()
        for d_val in diff_sequence:
            d_val = int(max(1, min(5, d_val)))
            questions = db.get_questions_by_filter(all_topics, d_val, exclude_ids=answered_ids, categories=categories)
            if questions:
                return self._package_question(random.choice(questions), d_val)

        return None

    def _package_question(self, q: dict, d_val: int) -> dict:
        options = q.get("options", [])[:]
        random.shuffle(options)
        return {
            **q,
            "options": options,
            "difficulty_label": self._get_difficulty_label(d_val)
        }

    def update_difficulty(self, current_diff: int, is_correct: bool, response_time: float, history: List[dict]) -> int:
        """
        Standard difficulty update logic (kept for compatibility or combined with trend).
        """
        if is_correct:
            if response_time < 20: return min(5, current_diff + 1)
            return current_diff
        else:
            if response_time > 45: return max(1, current_diff - 1)
            return max(1, current_diff - 1)

    def calculate_ability_score(self, accuracy: float, speed_score: float, difficulty: int) -> float:
        """
        Formula: (0.5 * Accuracy) + (0.3 * SpeedScore) + (0.2 * DifficultyLevel)
        """
        return (0.5 * accuracy) + (0.3 * speed_score) + (0.2 * (difficulty / 5 * 100))

    def detect_behavior(self, is_correct: bool, response_time: float) -> str:
        """
        Behavioral Pattern Detection
        """
        if is_correct:
            return "Strong mastery" if response_time < 20 else "Conceptual understanding (Low confidence)"
        else:
            return "Guessing behavior" if response_time < 10 else "Knowledge gap"

    def generate_recommendations(self, topic_stats: List[dict]) -> List[str]:
        recommendations = []
        for t in topic_stats:
            if t["accuracy"] < 50:
                recommendations.append(f"🔴 Revise basics of {t['topic']}. Focus on fundamental concepts.")
            elif t["accuracy"] < 75:
                recommendations.append(f"🟡 Practice medium-level problems in {t['topic']}.")
            else:
                recommendations.append(f"🟢 Great depth in {t['topic']}! Try advanced projects.")
        return recommendations

    def generate_competency_profile(self, session: dict) -> dict:
        responses = session["responses"]
        if not responses: return {}

        topics_hit = list(set(r["topic"] for r in responses))
        topic_stats = []
        
        total_correct = 0
        total_time = 0

        for topic in topics_hit:
            tr = [r for r in responses if r["topic"] == topic]
            correct = sum(1 for r in tr if r["is_correct"])
            avg_time = sum(r["response_time"] for r in tr) / len(tr)
            acc = (correct / len(tr)) * 100
            max_diff = max(r["difficulty"] for r in tr)
            
            topic_stats.append({
                "topic": topic,
                "questions_attempted": len(tr),
                "correct_answers": correct,
                "accuracy": int(round(acc)),
                "avg_response_time": int(round(avg_time)),
                "max_difficulty_reached": int(max_diff),
                "mastery_level": self._get_mastery_level(acc)
            })
            total_correct += correct
            total_time += sum(r["response_time"] for r in tr)

        overall_acc = (float(total_correct) / len(responses)) * 100
        
        # Enhanced: Include detailed answers for transparency
        detailed_responses = []
        for r in responses:
            q = db.get_question(r["question_id"])
            if not q: continue
            detailed_responses.append({
                "question": q.get("question_text", "Unknown Question"),
                "your_answer": r.get("selected_answer", "N/A"),
                "correct_answer": q.get("correct_answer", "N/A"),
                "is_correct": r.get("is_correct", False),
                "topic": q.get("topic", "N/A"),
                "type": q.get("type", "mcq")
            })

        # Advanced 5-Dimensional Metrics
        profile = {
            "session_id": session["session_id"],
            "total_questions": len(responses),
            "total_correct": total_correct,
            "overall_accuracy": int(round(overall_acc)),
            "overall_mastery": self._get_mastery_level(overall_acc),
            "avg_speed": int(round(total_time / len(responses))),
            "consistency": int(round(self._calculate_consistency(responses))),
            "topic_depth": int(round(sum(t["max_difficulty_reached"] for t in topic_stats) / len(topic_stats) * 20)),
            "behavioral_summary": self._generate_behavioral_summary(responses),
            "topics": topic_stats,
            "detailed_responses": detailed_responses,
            "recommendations": self.generate_recommendations(topic_stats)
        }
        return profile

    def _get_difficulty_label(self, d: int) -> str:
        return {1: "Beginner", 2: "Easy", 3: "Intermediate", 4: "Hard", 5: "Expert"}[d]

    def _get_mastery_level(self, acc: float) -> str:
        if acc >= 85: return "Expert 🏆"
        if acc >= 70: return "Advanced ⭐"
        if acc >= 50: return "Intermediate 📘"
        return "Beginner 🌱"

    def _calculate_consistency(self, responses: List[dict]) -> float:
        # Measure if accuracy is stable across the test
        if len(responses) < 4: return 80.0
        # Use a more robust split
        size = 3
        chunks = [responses[i:i + size] for i in range(0, len(responses), size)]
        accuracies = [float(sum(1 for r in c if r["is_correct"])) / len(c) for c in chunks]
        mean_acc = sum(accuracies) / len(accuracies)
        variance = sum((a - mean_acc)**2 for a in accuracies) / len(accuracies)
        return float(max(0.0, 100.0 - (variance * 500)))

    def _generate_behavioral_summary(self, responses: List[dict]) -> str:
        behaviors = [self.detect_behavior(r["is_correct"], r["response_time"]) for r in responses]
        most_common = max(set(behaviors), key=behaviors.count)
        return most_common
