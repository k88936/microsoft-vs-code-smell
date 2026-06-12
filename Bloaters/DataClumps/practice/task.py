from dataclasses import dataclass


@dataclass
class Achievement:
    home_lawn_security: bool
    roll_some_heads: bool
    sunny_days: bool

def print_achievement(user_name: str, achievement: Achievement, achievement_score:int) -> None:
    print(f"{user_name}"
          f"home_lawn_security: {achievement.home_lawn_security}, "
          f"roll_some_heads: {achievement.roll_some_heads}, "
          f"sunny_days: {achievement.sunny_days}, "
          f"score {achievement_score}")

def print_achievement(user_name: str, achievement: Achievement) -> None:
    score = evaluate_achievement(achievement)
    print(f"{user_name}"
          f"home_lawn_security: {achievement.home_lawn_security}, "
          f"roll_some_heads: {achievement.roll_some_heads}, "
          f"sunny_days: {achievement.sunny_days}, "
          f"score {score}")

def evaluate_achievement(achievement: Achievement) -> int:
    score = 0
    if achievement.home_lawn_security:
        score += 1
    if achievement.roll_some_heads:
        score += 2
    if achievement.sunny_days:
        score += 4
    return score