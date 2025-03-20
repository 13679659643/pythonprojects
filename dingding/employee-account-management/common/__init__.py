# -*- coding: utf-8 -*-
import hashlib
from .datetime_parse import universal_datetime_parse
from .numbers_parse import parse_mixed_decimal


class Utils:
    universal_time_parse = universal_datetime_parse
    parse_mixed_decimal = parse_mixed_decimal

    @classmethod
    def md5_encrypt(cls, text: str):
        md = hashlib.md5()
        md.update(text.encode('utf-8'))
        return md.hexdigest()

    @classmethod
    def replace_dict_key(cls, original: dict, rules: dict, only_keep_rules_keys: bool = True) -> dict:
        """
        替换字典key
        :param original: 原始字典
        :param rules: 替换规则字典
        :param only_keep_rules_keys: 是否只保留rules中的key
        :return: 替换键后的字典,{'a': 1, 'b': 2, 'c': 3}和{'a': 'x', 'b': 'y'}返回一个新的字典{'x': 1, 'y': 2}
        """
        # 创建一个新字典用于存放替换键后的项
        new_dict = {}
        for key, value in original.items():
            if only_keep_rules_keys and key not in rules:
                continue
            # 如果键在替换规则中，使用新的键
            new_key = rules.get(key, key)
            new_dict[new_key] = value

        return new_dict

    @classmethod
    def mark_unique_index(cls, data_package: list[dict], fields: list[str] = None):
        """
        功能: 相同数据增加唯一标识字段unique_index, 从1自增加1
        :param data_package: 数据包
        :param fields: 根据字段增加唯一标识, 不传取所有字段
        :return: 处理后的数据包
        """

        # 根据字段拼接字符串索引
        def _index_str(record, fields):
            return '_INDEX_STR//:' + ','.join(str(record.get(field, '')) for field in fields)

        # 辅助字典存储每个索引对应的计数器
        unique_index_counter = {}

        # 处理数据包
        result_package = []
        for data in data_package:
            try:
                index_fields = fields or list(data.keys())
                unique_str = _index_str(data, index_fields)

                if unique_str not in unique_index_counter:
                    unique_index_counter[unique_str] = 1  # 初始化为1

                data['unique_index'] = str(unique_index_counter[unique_str])
                unique_index_counter[unique_str] += 1

            except KeyError as e:
                print(f"Warning: Field {e} not found in record, skipping...")
                continue

            result_package.append(data)

        return result_package

    @classmethod
    def camel_to_snake(cls, s):
        return ''.join(['_' + c.lower() if c.isupper() else c for c in s]).lstrip('_')


if __name__ == '__main__':
    Utils = Utils()
    print(Utils.md5_encrypt('123456'))
    print(Utils.replace_dict_key({'a': 1, 'b': 2, 'c': 3}, {'a': 'x', 'b': 'y'}, False))
