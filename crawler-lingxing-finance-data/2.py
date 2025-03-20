from datetime import datetime


def generate_month_list(start, end):
    start_date = datetime.strptime(start, "%Y%m")
    end_date = datetime.strptime(end, "%Y%m")

    current_date = start_date
    result = []

    while current_date <= end_date:
        result.append(current_date.strftime("%Y%m"))
        # 增加一个月
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)

    return result


print(generate_month_list('202407','202407'))