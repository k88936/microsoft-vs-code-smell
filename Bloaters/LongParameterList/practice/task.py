from dataclasses import dataclass

@dataclass
class Achievement:
    home_lawn_security: bool
    roll_some_heads: bool
    sunny_days: bool




def print_achievement(user_name: str, achievement: Achievement) -> None:
    score = evaluate_achievement(achievement)
    print(f"{user_name}\n"
          f"home_lawn_security: {achievement.home_lawn_security},\n"
          f"roll_some_heads: {achievement.roll_some_heads},\n"
          f"sunny_days: {achievement.sunny_days},\n"
          f"score {score}\n")


def evaluate_achievement(achievement: Achievement) -> int:
    score = 0
    if achievement.home_lawn_security:
        score += 1
    if achievement.roll_some_heads:
        score += 2
    if achievement.sunny_days:
        score += 4
    return score


if __name__ == "__main__":
    user_name = "Crazy Dave"
    home_lawn_security = True
    roll_some_heads = False
    sunny_days = True

    achievement = Achievement(home_lawn_security=home_lawn_security,
                              roll_some_heads=roll_some_heads,
                              sunny_days=sunny_days)
    print_achievement(user_name, achievement)
