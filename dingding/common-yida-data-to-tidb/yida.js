/**
 WLD-预决算提报\IPD-预决算提报
 */
// export function budgetList({ value = [] }) {
//   //  预算金额：
//   let Budget = 0;
//   //   实际执行金额：
//   let ActualexecutionAmount = 0;
//   //   差异金额：
//   let DifferenceInAmount = 0;
//
//   // 如果数组第一项是"合计"，则移除
//   if (value[0].selectField_llorhprr === "合计") {
//     value.shift();
//   }
//
//   // 确保value是可迭代的
//   if (Array.isArray(value)) {
//     // 遍历子表单中的所有数据
//     for (let item of value) {
//       // 检查预算金额字段是否存在且为数字，避免出现非数字的错误
//       if (item.hasOwnProperty('numberField_llorhprs') && !isNaN(Number(item.numberField_llorhprs))) {
//         // 预算金额：
//         Budget += Number(item.numberField_llorhprs);
//       }
//       if (item.hasOwnProperty('numberField_llorhprt') && !isNaN(Number(item.numberField_llorhprt))) {
//         // 实际执行金额：
//         ActualexecutionAmount += Number(item.numberField_llorhprt);
//       }
//       if (item.hasOwnProperty('numberField_llorhpru') && !isNaN(Number(item.numberField_llorhpru))) {
//         // 差异金额：
//         DifferenceInAmount += Number(item.numberField_llorhpru);
//       }
//     }
//   } else {
//     console.error("value is not iterable");
//   }
//
//   // 添加新的"合计"项目到数组的开始
//   value.unshift({
//     selectField_llorhprr: "合计",
//     numberField_llorhprs: Budget,
//     numberField_llorhprt: ActualexecutionAmount,
//     numberField_llorhpru: DifferenceInAmount,
//     textareaField_llorhprv: ""
//   });
//
//   // 返回更新后的数据
//   return value;
// }

/**
 LMD-预决算提报、DSD-预决算提报、GMO-预决算提报
 LVD-预决算提报_复制\资金科-预决算提报
 */
// export function budgetList({ value = [] }) {
//   //  预算金额：
//   let Budget = 0;
//   //   实际执行金额：
//   let ActualexecutionAmount = 0;
//   //   差异金额：
//   let DifferenceInAmount = 0;
//
//   // 如果数组第一项是"合计"，则移除
//   if (value[0].selectField_llotk0lw === "合计") {
//     value.shift();
//   }
//
//   // 确保value是可迭代的
//   if (Array.isArray(value)) {
//     // 遍历子表单中的所有数据
//     for (let item of value) {
//       // 检查预算金额字段是否存在且为数字，避免出现非数字的错误
//       if (item.hasOwnProperty('numberField_llotk0lx') && !isNaN(Number(item.numberField_llotk0lx))) {
//         // 预算金额：
//         Budget += Number(item.numberField_llotk0lx);
//       }
//       if (item.hasOwnProperty('numberField_llotk0ly') && !isNaN(Number(item.numberField_llotk0ly))) {
//         // 实际执行金额：
//         ActualexecutionAmount += Number(item.numberField_llotk0ly);
//       }
//       if (item.hasOwnProperty('numberField_llotk0lz') && !isNaN(Number(item.numberField_llotk0lz))) {
//         // 差异金额：
//         DifferenceInAmount += Number(item.numberField_llotk0lz);
//       }
//     }
//   } else {
//     console.error("value is not iterable");
//   }
//
//   // 添加新的"合计"项目到数组的开始
//   value.unshift({
//     selectField_llotk0lw: "合计",
//     numberField_llotk0lx: Budget,
//     numberField_llotk0ly: ActualexecutionAmount,
//     numberField_llotk0lz: DifferenceInAmount,
//     textareaField_llotk0m0: ""
//   });
//
//   // 返回更新后的数据
//   return value;
// }

// LVD收费比例提报
export function budgetList({value = []}) {
    //  LVD收费比例-工作量占比：
    let WorkloadRatio = 0;

    // 如果数组第一项是"合计"，则移除
    if (value[0].selectField_lme6omf1 === "合计") {
        value.shift();
    }

    // 确保value是可迭代的
    if (Array.isArray(value)) {
        // 遍历子表单中的所有数据
        for (let item of value) {
            // 检查预算金额字段是否存在且为数字，避免出现非数字的错误
            if (item.hasOwnProperty('textField_lme6omex') && !isNaN(Number(item.textField_lme6omex))) {
                // 预算金额：
                WorkloadRatio += Number(item.textField_lme6omex.replace('%', ''));
            }
        }
    } else {
        console.error("value is not iterable");
    }

    // 添加新的"合计"项目到数组的开始
    value.unshift({
        selectField_lme6omf1: "合计",
        textField_lme6omex: WorkloadRatio + "%"
    });

    // 返回更新后的数据
    return value;
}