class ScoringService:
    def __init__(self, max_attempts: int, penalty_cap: int) -> None:
        if max_attempts < 1:
            raise ValueError("Max attempts must be greater or equal than 1")

        if penalty_cap < 0:
            raise ValueError("Penalty cap must be greater or equal than 0")

        self.penalty_cap = penalty_cap
        self.penalty_step = penalty_cap / (max_attempts - 1) if max_attempts > 1 else 0

    # Можно добавить влияние плагиата на баллы
    def calculate(
        self, tests_passed: int, tests_total: int, attempt_number: int
    ) -> int:
        if tests_total == 0:
            return 0

        base_score = (tests_passed / tests_total) * 100
        attempt_penalty = min(
            self.penalty_cap, (attempt_number - 1) * self.penalty_step
        )
        score = base_score - attempt_penalty
        score = max(0, min(100, score))
        return round(score)
