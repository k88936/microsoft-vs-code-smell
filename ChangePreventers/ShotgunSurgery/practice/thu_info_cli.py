from argparse import ArgumentParser
from dataclasses import dataclass

from CodeSmell.ShotgunSurgery.practice.i18n import I18nKey, I18nLanguage, set_language, t


@dataclass(frozen=True)
class Profile:
    id: int
    name: str

mock_dorm_info = {
    "score": 100,
    "stars": 5
}

mock_sports_info = {
    "swim_passed": True,
    "reservation_score": 100
}


def get_dorm_info(profile: Profile) -> str:
    info = mock_dorm_info
    score_line = t(I18nKey.DORM_SCORE, name=profile.name, score=info["score"])
    stars_line = t(I18nKey.DORM_STARS, stars=info["stars"])
    return f"{score_line}\n {stars_line}"


def get_sports_info(profile: Profile) -> str:
    info = mock_sports_info
    swim_result = t(I18nKey.PASSED if info['swim_passed'] else I18nKey.FAILED)
    swim_line = t(I18nKey.SWIM_RESULT, name=profile.name, result=swim_result)
    score_line = t(I18nKey.SPORTS_SCORE, score=info['reservation_score'])
    return f"{swim_line}\n {score_line}"


def main() -> None:
    parser = ArgumentParser(description="THU Info CLI")
    parser.add_argument("--id", type=int, required=True, help="Student ID")
    parser.add_argument("--name", type=str, required=True, help="Student name")
    parser.add_argument("--lang", choices=["zh", "en"], default="zh", help="Language")

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("dorm", help="Get dormitory info")
    subparsers.add_parser("sports", help="Get sports info")

    args = parser.parse_args()

    set_language(I18nLanguage.ZH if args.lang == "zh" else I18nLanguage.EN)

    profile = Profile(id=args.id, name=args.name)
    match args.command:
        case "dorm":
            print(get_dorm_info(profile))
        case "sports":
            print(get_sports_info(profile))


if __name__ == "__main__":
    main()
