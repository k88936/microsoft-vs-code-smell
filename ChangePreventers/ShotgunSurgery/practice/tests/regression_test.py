import unittest

from CodeSmell.ShotgunSurgery.practice.thu_info_cli import Profile, get_dorm_info, get_sports_info
from CodeSmell.ShotgunSurgery.practice.i18n import set_language, I18nLanguage


def print_all():
    profile = Profile(id=2024000000, name="王小明")
    return get_dorm_info(profile) + '\n' + get_sports_info(profile)


class TestCase(unittest.TestCase):

    def test_en(self):

        try:
            from CodeSmell.ShotgunSurgery.practice.thu_info_cli import set_lang
            set_lang("en")
        except:
            pass
        set_language(I18nLanguage.EN)

        output = print_all()
        print(output)
        assert '王小明' in output
        assert 'dorm' in output
        assert 'swim' in output

    def test_zh(self):

        try:
            from CodeSmell.ShotgunSurgery.practice.thu_info_cli import set_lang
            set_lang("zn")
        except:
            pass
        set_language(I18nLanguage.ZH)

        output = print_all()
        print(output)
        assert '王小明' in output
        assert '宿舍' in output
        assert '游泳' in output
