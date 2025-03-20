# -*- coding: utf-8 -*-
# @Time     : 2024/11/07 17:30
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : datetime_parse.py

from dateutil import parser
from dateutil.tz import gettz


# 这一坨是做时间解析的

# 时区信息 不够自己加
DATE_TIME_TZINFOS = {
    'UTC': gettz('UTC'),
    "PDT": gettz('America/Los_Angeles'),
    'PST': gettz('America/Los_Angeles'),
    'JST': gettz('Asia/Tokyo'),
}
# 添加 GMT 偏移量
for i in range(-12, 15):  # 从 -12 到 +14
    tz_key = f'GMT{i:+}'
    DATE_TIME_TZINFOS[tz_key] = gettz(f'Etc/GMT{i:+}')

# 日期解析配置
DATE_TIME_PARSE_CONFIG = {
    # 美国
    'US': {
        'dayfirst': False,  # 优先考虑(日月-True 年-False, 月日-False 年-False)格式，默认为False
        'yearfirst': False,  # 优先考虑(年-True 日月-True, 年-True 月日-False)格式，默认为False
        'is_need_translation': False,  # 是否需要翻译月份，默认为True
    },
    # 加拿大
    'CA': {
        'dayfirst': False,   # 优先考虑(日月-True 年-False, 月日-False 年-False)格式，默认为False
        'yearfirst': False,  # 优先考虑(年-True 日月-True, 年-True 月日-False)格式，默认为False
        'is_need_translation': False,  # 是否需要翻译月份，默认为True
    },
    # 墨西哥
    'MX': {
        'dayfirst': True,  # 优先考虑(日月-True 年-False, 月日-False 年-False)格式，默认为False
        'yearfirst': False,  # 优先考虑(年-True 日月-True, 年-True 月日-False)格式，默认为False
        'is_need_translation': True,  # 是否需要翻译月份，默认为True
        'month_translation': {
            'ene': 'Jan',
            'feb': 'Feb',
            'mar': 'Mar',
            'abr': 'Apr',
            'may': 'May',
            'jun': 'Jun',
            'jul': 'Jul',
            'ago': 'Aug',
            'sep': 'Sep',
            'oct': 'Oct',
            'nov': 'Nov',
            'dic': 'Dec',
        }
    },
    # 英国
    'UK': {
        'dayfirst': True,  # 优先考虑(日月-True 年-False, 月日-False 年-False)格式，默认为False
        'yearfirst': False,  # 优先考虑(年-True 日月-True, 年-True 月日-False)格式，默认为False
        'is_need_translation': False,  # 是否需要翻译月份，默认为True
    },
    # 德国
    'DE': {
        'dayfirst': True,  # 优先考虑(日月-True 年-False, 月日-False 年-False)格式，默认为False
        'yearfirst': False,  # 优先考虑(年-True 日月-True, 年-True 月日-False)格式，默认为False
        'is_need_translation': False,  # 是否需要翻译月份，默认为True
    },
    # 法语
    'FR': {
        'dayfirst': True,  # 优先考虑(日月-True 年-False, 月日-False 年-False)格式，默认为False
        'yearfirst': False,  # 优先考虑(年-True 日月-True, 年-True 月日-False)格式，默认为False
        'is_need_translation': True,  # 是否需要翻译月份，默认为True
        'month_translation': {
            'janv': 'Jan',
            'févr': 'Feb',
            'mars': 'Mar',
            'avr': 'Apr',
            'mai': 'May',
            'juin': 'Jun',
            'juil': 'Jul',
            'août': 'Aug',
            'sept': 'Sep',
            'oct': 'Oct',
            'nov': 'Nov',
            'déc': 'Dec', }
    },
    # 意大利
    'IT': {
        'dayfirst': True,  # 优先考虑(日月-True 年-False, 月日-False 年-False)格式，默认为False
        'yearfirst': False,  # 优先考虑(年-True 日月-True, 年-True 月日-False)格式，默认为False
        'is_need_translation': True,  # 是否需要翻译月份，默认为True
        'month_translation': {
            'gen': 'Jan',
            'feb': 'Feb',
            'mar': 'Mar',
            'apr': 'Apr',
            'mag': 'May',
            'giu': 'Jun',
            'lug': 'Jul',
            'ago': 'Aug',
            'set': 'Sep',
            'ott': 'Oct',
            'nov': 'Nov',
            'dic': 'Dec',
            'août': 'Aug',
        }  # 月份翻译
    },
    # 西班牙
    'ES': {
        'dayfirst': True,  # 优先考虑(日月-True 年-False, 月日-False 年-False)格式，默认为False
        'yearfirst': False,  # 优先考虑(年-True 日月-True, 年-True 月日-False)格式，默认为False
        'is_need_translation': True,  # 是否需要翻译月份，默认为True
        'month_translation': {
            'ene': 'Jan',
            'feb': 'Feb',
            'mar': 'Mar',
            'abr': 'Apr',
            'may': 'May',
            'jun': 'Jun',
            'jul': 'Jul',
            'ago': 'Aug',
            'sept': 'Sep',
            'oct': 'Oct',
            'nov': 'Nov',
            'dic': 'Dec',
        }
    },
    # 法语-比利时
    'BE': {
        'dayfirst': True,  # 优先考虑(日月-True 年-False, 月日-False 年-False)格式，默认为False
        'yearfirst': False,  # 优先考虑(年-True 日月-True, 年-True 月日-False)格式，默认为False
        'is_need_translation': True,
        'month_translation': {
            'janv': 'Jan',
            'févr': 'Feb',
            'mars': 'Mar',
            'avr': 'Apr',
            'mai': 'May',
            'juin': 'Jun',
            'juil': 'Jul',
            'août': 'Aug',
            'sept': 'Sep',
            'oct': 'Oct',
            'nov': 'Nov',
            'déc': 'Dec',
        }
    },
    # 波兰
    'PL': {
        'dayfirst': True,  # 优先考虑(日月-True 年-False, 月日-False 年-False)格式，默认为False
        'yearfirst': False,  # 优先考虑(年-True 日月-True, 年-True 月日-False)格式，默认为False
        'is_need_translation': True,  # 是否需要翻译月份，默认为True
        'month_translation': {
            'sty': 'Jan',
            'lut': 'Feb',
            'mar': 'Mar',
            'kwi': 'Apr',
            'maj': 'May',
            'cze': 'Jun',
            'lip': 'Jul',
            'sie': 'Aug',
            'wrz': 'Sep',
            'paź': 'Oct',
            'lis': 'Nov',
            'gru': 'Dec',
        }
    },
    # 瑞典
    'SE': {
        'dayfirst': True,  # 优先考虑(日月-True 年-False, 月日-False 年-False)格式，默认为False
        'yearfirst': False,  # 优先考虑(年-True 日月-True, 年-True 月日-False)格式，默认为False
        'is_need_translation': True,  # 是否需要翻译月份，默认为True
        'month_translation': {
            'jan': 'Jan',
            'feb': 'Feb',
            'mar': 'Mar',
            'apr': 'Apr',
            'maj': 'May',
            'jun': 'Jun',
            'jul': 'Jul',
            'aug': 'Aug',
            'sep': 'Sep',
            'okt': 'Oct',
            'nov': 'Nov',
            'dec': 'Dec',
        }
    },
    # 日本
    'JP': {
        'dayfirst': False,  # 优先考虑(日月-True 年-False, 月日-False 年-False)格式，默认为False
        'yearfirst': True,  # 优先考虑(年-True 日月-True, 年-True 月日-False)格式，默认为False
        'is_need_translation': False,  # 是否需要翻译月份，默认为True
    },
    # 土耳其
    'TR': {
        'dayfirst': True,  # 优先考虑(日月-True 年-False, 月日-False 年-False)格式，默认为False
        'yearfirst': False,  # 优先考虑(年-True 日月-True, 年-True 月日-False)格式，默认为False
        'is_need_translation': True,  # 是否需要翻译月份，默认为True
        'month_translation': {
            'ocak': 'Jan',
            'subat': 'Feb',
            'mart': 'Mar',
            'nisan': 'Apr',
            'mayıs': 'May',
            'haziran': 'Jun',
            'temmuz': 'Jul',
            'ağustos': 'Aug',
            'eylül': 'Sep',
            'ekim': 'Oct',
            'kasım': 'Nov',
            'aralık': 'Dec',
        }
    }
}


# 标准化时间格式
def universal_datetime_parse(date_time, country_code, dayfirst: bool = None, yearfirst: bool = None):
    """
    解析日期时间字符串，并返回ISO格式的时间。

    :param date_time: 需要解析的日期时间字符串
    :param country_code: 国家/地区代码，仅当special为True时有效
    :param dayfirst: # 优先考虑(日月-True 年-False, 月日-False 年-False)格式，默认为False
    :param yearfirst: # 优先考虑(年-True 日月-True, 年-True 月日-False)格式，默认为False

    :return: ISO格式的时间字符串
    """
    # 根据国家/地区代码获取日期时间解析配置
    date_time_config = DATE_TIME_PARSE_CONFIG[country_code.upper()]

    # 如果配置中指定了需要翻译日期时间字符串，则执行翻译
    if date_time_config['is_need_translation']:
        # 根据国家/地区代码翻译月份名称
        for ita_month, eng_month in date_time_config['month_translation'].items():
            if ita_month in date_time:
                date_time = date_time.replace(ita_month, eng_month)
                break

    # 解析日期时间字符串，并返回ISO格式的时间
    return parser.parse(
        date_time,
        tzinfos=DATE_TIME_TZINFOS,
        dayfirst=date_time_config['dayfirst'] if dayfirst is None else dayfirst,
        yearfirst=date_time_config['yearfirst'] if yearfirst is None else yearfirst
    ).isoformat()


if __name__ == '__main__':

    iso_date = universal_datetime_parse('1 mar 2024 2:10:17 UTC', 'es', dayfirst=True, yearfirst=False)
    print(iso_date)
