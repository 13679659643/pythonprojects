# -*- coding: utf-8 -*-
# @Time     : 2024/11/07 17:34
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : numbers_parse.py

from babel.numbers import parse_decimal

# 解析货币金额

# 国家代码映射语言代码
LOCALE_ALIASES = {
    'ae': 'ar_AE',
    'au': 'en_AU',
    'es': 'es_ES',
    'pl': 'pl_PL',
    'se': 'sv_SE',
    'de': 'de_DE',
    'uk': 'uk_UA',
    'nl': 'nl_NL',
    'it': 'it_IT',
    'fr': 'fr_FR',
    'be': 'fr_BE',
    'jp': 'ja_JP',
    'ca': 'en_CA',
    'mx': 'en_US',
    'br': 'pt_BR',
    'us': 'en_US',
    'sa': 'ar_SA',
    'sg': 'en_SG',
    'tr': 'tr_TR',
}

# 货币符号和数字分隔符
country_rules = {
    'AE': {'decimal': '.', 'thousands': ','},
    'AU': {'decimal': '.', 'thousands': ','},
    'ES': {'decimal': ',', 'thousands': '.'},   # 西班牙
    'PL': {'decimal': ',', 'thousands': '.'},   # 波兰
    'SE': {'decimal': ',', 'thousands': '.'},   # 瑞典
    'DE': {'decimal': ',', 'thousands': '.'},   # 德国
    'UK': {'decimal': '.', 'thousands': ','},   # 英国
    'NL': {'decimal': '.', 'thousands': ','},   # 荷兰
    'IT': {'decimal': ',', 'thousands': '.'},   # 意大利
    'FR': {'decimal': ',', 'thousands': ' '},   # 法国
    'BE': {'decimal': ',', 'thousands': '.'},   # 比利时
    'JP': {'decimal': '.', 'thousands': ','},   # 日本
    'CA': {'decimal': '.', 'thousands': ','},   # 加拿大
    'MX': {'decimal': '.', 'thousands': ','},   # 墨西哥
    'BR': {'decimal': ',', 'thousands': '.'},
    'US': {'decimal': '.', 'thousands': ','},   # 美国
    'SA': {'decimal': '.', 'thousands': ','},
    'SG': {'decimal': '.', 'thousands': ','},
    'TR': {'decimal': '.', 'thousands': ','},
}


def parse_mixed_decimal(string, locale):
    """
    解析混合小数格式的字符串。

    本函数旨在处理不同国家/地区的小数格式。它首先根据提供的地区信息获取相应的格式规则，
    如果地区无效，则抛出一个错误。随后，函数检查输入字符串是否符合混合格式（即包含小数点但没有逗号），
    并相应地调整小数分隔符。最后，使用解析函数将格式化的字符串转换为小数值。

    参数:
    string (str): 需要解析的字符串，可能包含混合的小数格式。
    locale (str): 表示国家/地区的字符串，用于确定小数格式规则。

    返回:
    decimal: 解析后的十进制数值。

    抛出:
    ValueError: 如果提供的地区不受支持。
    """
    string = str(string).strip()
    # 获取指定地区的格式规则
    rules = country_rules.get(locale)
    # 如果没有找到对应的规则，抛出错误
    if not rules:
        raise ValueError(f"Unsupported locale: {locale}")

    # 处理混合格式的小数分隔符
    # 如果字符串中包含小数点（.）但没有逗号（,），则将其替换为该地区对应的货币符号
    if '.' in string and ',' not in string:
        string = string.replace('.', rules['decimal'])

    # 使用解析函数将格式化后的字符串转换为小数值
    value = parse_decimal(string, locale=LOCALE_ALIASES[locale.lower()])
    return value



if __name__ == '__main__':
    # 示例：处理不同国家格式的数字
    value2 = parse_mixed_decimal('5.9000,66', locale='MX')
    print(value2)  # 应该输出: Decimal('-5.90')
