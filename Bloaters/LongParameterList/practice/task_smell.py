def print_achievement(user_name: str,
                      home_lawn_security: bool,
                      roll_some_heads: bool,
                      sunny_days: bool,
                      achievement_score: float) -> None:
    print(f"{user_name}\n"
          f"home_lawn_security: {home_lawn_security}, \n"
          f"roll_some_heads: {roll_some_heads}, \n"
          f"sunny_days: {sunny_days}, \n"
          f"score: {achievement_score}\n")


def evaluate_achievement(home_lawn_security: bool, roll_some_heads: bool, sunny_days: bool) -> int:
    score = 0
    if home_lawn_security:
        score += 1
    if roll_some_heads:
        score += 2
    if sunny_days:
        score += 4
    return score
