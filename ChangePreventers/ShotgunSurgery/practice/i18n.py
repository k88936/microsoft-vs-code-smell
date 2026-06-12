from dataclasses import dataclass
from enum import Enum
@dataclass(frozen=True)
class _I18nEntry:
    zh: str
    en: str

class I18nKey(Enum):
    GREETING = _I18nEntry(zh="你好，{name}！", en="Hello, {name}!")
    PASSED = _I18nEntry(zh="已通过",en="passed")
    FAILED = _I18nEntry(zh="未通过",en="failed")
    DORM_SCORE = _I18nEntry(zh="{name}, 你的宿舍评分为: {score}", en="{name}, your dorm score is: {score}")
    DORM_STARS = _I18nEntry(zh="你的宿舍是{stars}星好宿舍", en="your dorm is {stars} stars")
    SWIM_RESULT = _I18nEntry(zh="{name}, 你的游泳测试{result}", en="{name}, your swimming test is {result}")
    SPORTS_SCORE = _I18nEntry(zh="你的体育预约评分为: {score}", en="your sports reservation score is: {score}")

class I18nLanguage(Enum):
    ZH = "zh-CN"
    EN = "en-US"

_current_lang: I18nLanguage = I18nLanguage.ZH

def set_language(lang: I18nLanguage) -> None:
    """
    set global translation language
    """
    global _current_lang
    _current_lang = lang

def t(key: I18nKey, **params: object) -> str:
    """
    translate str, supporting template
    """
    entry: _I18nEntry = key.value

    match _current_lang:
        case I18nLanguage.EN:
            template = entry.en
        case I18nLanguage.ZH:
            template = entry.zh

    if not params:
        return template

    result = template
    for k, v in params.items():
        v = str(v)
        result = result.replace("{" + k + "}", v)
    return result

if __name__ == "__main__":
    set_language(I18nLanguage.EN)
    print(t(I18nKey.GREETING, name="World"))
    set_language(I18nLanguage.ZH)
    print(t(I18nKey.GREETING, name="世界"))
