export function budgetList({ value = [] }) {
  //  数量：
  let number = 0;

  // 如果数组第一项是"合计"，则移除
  if (value[0].textField_lqg7yqw3 === "合计") {
    value.shift();
  }

  // 确保value是可迭代的
  if (Array.isArray(value)) {
    // 遍历子表单中的所有数据
    for (let item of value) {
      // 检查预算金额字段是否存在且为数字，避免出现非数字的错误
      if (item.hasOwnProperty('numberField_lqg9t6sc') && !isNaN(Number(item.numberField_lqg9t6sc))) {
        // 预算金额：
        number += Number(item.numberField_lqg9t6sc);
      }

    }
  } else {
    console.error("value is not iterable");
  }

  // 添加新的"合计"项目到数组的开始
  value.unshift({
    textField_lqg7yqw3: "合计",
    numberField_lqg9t6sc: number,
    textField_lqg7yqw4: "合计",
    textField_lqg7yqw5: "合计",
    textField_lqg7yqw7: "弃置原因见下方详情"
  });

  // 返回更新后的数据
  return value;
}

export function onChange({ value, extra }){
  //  数量：
  let number = 0;

  // 如果数组第一项是"合计"，则移除
  if (value[0].textField_lqg7yqwa === "合计") {
    value.shift();
  }

  // 确保value是可迭代的
  if (Array.isArray(value)) {
    // 遍历子表单中的所有数据
    for (let item of value) {
      // 检查预算金额字段是否存在且为数字，避免出现非数字的错误
      if (item.hasOwnProperty('numberField_lqg9t6sb') && !isNaN(Number(item.numberField_lqg9t6sb))) {
        // 预算金额：
        number += Number(item.numberField_lqg9t6sb);
      }

    }
  } else {
    console.error("value is not iterable");
  }

  // 添加新的"合计"项目到数组的开始
  value.unshift({
    textField_lqg7yqwa: "合计",
    numberField_lqg9t6sb: number,
    textField_lqg7yqwc: "弃置原因见下方详情"
  });

  // 返回更新后的数据
  return value;
}