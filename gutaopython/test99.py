import re


# 正则提取替换字符串：匹配 <br\/> 或 <br/> 标签并替换为空格
@staticmethod
def extract_replace_str(item):
    """
    从给定的字符串中提取字符串，去掉 HTML 换行标签。
    参数:
    item (str): 需要提取替换的字符串。
    返回:
    str: 提取并格式化后的字符。
    <br 匹配 <br。
    \s* 匹配零个或多个空白字符（包括空格、制表符等）。
    \/? 匹配零个或一个 /。
    > 匹配 >。
    """
    # 定义正则表达式模式，匹配 <br\/> 或 <br/> 标签
    pattern = r'<br\s*\/?>'

    # 使用 re.sub 替换掉匹配的 HTML 换行标签
    cleaned_text = re.sub(pattern, ' ', item)

    return cleaned_text


# 提取html中相关信息,并格式化字符.
@staticmethod
def extract_html_info(html):
    """
    从给定的 HTML 字符串中提取物流信息。

    参数:
    html (str): 包含需要信息的 HTML 字符串。

    返回:
    str: 提取并格式化后的HTML信息字符串。
    """
    # 定义正则表达式模式：
    # 匹配物流公司名称：(.*?)：捕获从字符串开始到 <br/> 标签之间的所有字符。
    carrier_pattern = r'^(.*?)<br\/>'
    # 匹配追踪号码：(.*?)：捕获 <a> 标签中的内容。
    tracking_number_pattern = r'<a[^>]*?class="outer_carrier_tracking_number"[^>]*?>(.*?)<\/a>'
    # 匹配URL：([^"]*?)：捕获 href 属性中的 URL。
    url_pattern = r'<a[^>]*?href="([^"]*?)"[^>]*?>'

    # 提取物流公司名称：strip()去除前后的空白字符
    carrier_match = re.search(carrier_pattern, html)
    carrier = carrier_match.group(1).strip() if carrier_match else ""

    # 提取追踪号码
    tracking_number_match = re.search(tracking_number_pattern, html)
    tracking_number = tracking_number_match.group(1).strip() if tracking_number_match else ""

    # 提取URL
    url_match = re.search(url_pattern, html)
    url = url_match.group(1).strip() if url_match else ""

    # 如果没有找到追踪号码和URL，检查是否有简单的格式
    if not tracking_number and not url:
        # 尝试匹配简单格式
        simple_pattern = r'<br\/>(.*)$'
        simple_match = re.search(simple_pattern, html)
        tracking_number = simple_match.group(1).strip() if simple_match else ""

    # 格式化结果
    result = f"{carrier} {tracking_number} {url}".strip()
    return result

# 示例用法
html_input = "OTHER<br/>卡派橙IND4"
formatted_info = extract_html_info(html_input)
print(
    formatted_info)  # 输出: UPS 1ZC600A30327513700 https://wwwapps.ups.com/WebTracking/track?loc=zh_CN&track.x=Track&trackNums=1ZC600A30327513700
