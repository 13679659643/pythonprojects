/**
 * 尊敬的用户，你好：页面 JS 面板是高阶用法，一般不建议普通用户使用，如需使用，请确定你具备研发背景，能够自我排查问题。当然，你也可以咨询身边的技术顾问或者联系宜搭平台的技术支持获得服务（可能收费）。
 * 我们可以用 JS 面板来开发一些定制度高功能，比如：调用阿里云接口用来做图像识别、上报用户使用数据（如加载完成打点）等等。
 * 你可以点击面板上方的 「使用帮助」了解。
 */

// 当页面渲染完毕后马上调用下面的函数，这个函数是在当前页面 - 设置 - 生命周期 - 页面加载完成时中被关联的。
export function didMount() {
    console.log(`「页面 JS」：当前页面地址 ${location.href}`);
    // console.log(`「页面 JS」：当前页面 id 参数为 ${this.state.urlParams.id}`);
    // 更多 this 相关 API 请参考：https://www.yuque.com/yida/support/ocmxyv#OCEXd
    // document.title = window.loginUser.userName + ' | 宜搭';
}

/**
 * TableField onChange
 */
//

export function budgetList({value = []}) {
    let SalesTarget = 0; //销售额目标  numberField_licip9pq
    let GrossProfitTarget = 0; //毛利额目标  numberField_licip9pr
    let GrossProfitRedLine = 0; //毛利额红线 numberField_ln2kpxpb
    let ProductSalesVolume = 0; //商品销量  numberField_ln2kpxpc
    let ProductCost = 0; //货品成本 numberField_ln2kpxpd
    let ShippingCost = 0; //配送费用  numberField_ln2kpxpe
    let WarehousingCost = 0; //仓储费用 numberField_ln2kpxpf
    let ProductSubsidy = 0; //商品补贴  numberField_ln2kpxpg
    let AdvertisingExpenses = 0; //广告费用 numberField_licip9px
    let ReplenishmentPrincipal = 0; //补单本金  numberField_licip9pz
    let ReplenishmentCost = 0; //补单费用 numberField_licip9q0
    let VINEEvaluationCost = 0; //VINE评费用 numberField_ln2kpxpp
    let OtherPromotions = 0; //其它推广 numberField_licip9py
    let DeliverrBudget = 0; //deliverr预算  numberField_licip9q3
    let OtherBudgets = 0; //其他预算  numberField_licip9q4
    let GrossProfitMarginTarget = 0; //毛利率目标  numberField_licip9q7 = GrossProfitTarget / SalesTarget
    let MarketingExpenses = 0; //营销费用 numberField_ln2kpxph = AdvertisingExpenses + ReplenishmentPrincipal + VINEEvaluationCost + OtherPromotions
    let ProductCostRatio = 0; //货品成本占比  numberField_ln2kpxpi = ProductCost / SalesTarget
    let ShippingCostRatio = 0; //配送费用占比 numberField_ln2kpxpj = ShippingCost / SalesTarget
    let WarehousingCostRatio = 0; //仓储费用占比  numberField_ln2kpxpk = WarehousingCost / SalesTarget
    let MarketingCostRatio = 0; //营销费用占比  numberField_ln2kpxpl = MarketingExpenses / SalesTarget

    // 如果数组第一项是"合计"，则移除
    if (value[0].textField_licip9pp === "合计") {
        value.shift();
    }
    // 确保value是可迭代的
    if (Array.isArray(value)) {
        // 遍历子表单中的所有数据
        for (let item of value) {
            // 检查预算金额字段是否存在且为数字，避免出现非数字的错误
            if (item.hasOwnProperty('numberField_licip9pq') && !isNaN(Number(item.numberField_licip9pq))) {
                SalesTarget += Number(item.numberField_licip9pq);
            }
            if (item.hasOwnProperty('numberField_licip9pr') && !isNaN(Number(item.numberField_licip9pr))) {
                GrossProfitTarget += Number(item.numberField_licip9pr);
            }
            if (item.hasOwnProperty('numberField_ln2kpxpb') && !isNaN(Number(item.numberField_ln2kpxpb))) {
                GrossProfitRedLine += Number(item.numberField_ln2kpxpb);
            }
            if (item.hasOwnProperty('numberField_ln2kpxpc') && !isNaN(Number(item.numberField_ln2kpxpc))) {
                ProductSalesVolume += Number(item.numberField_ln2kpxpc);
            }
            if (item.hasOwnProperty('numberField_ln2kpxpd') && !isNaN(Number(item.numberField_ln2kpxpd))) {
                ProductCost += Number(item.numberField_ln2kpxpd);
            }
            if (item.hasOwnProperty('numberField_ln2kpxpe') && !isNaN(Number(item.numberField_ln2kpxpe))) {
                ShippingCost += Number(item.numberField_ln2kpxpe);
            }
            if (item.hasOwnProperty('numberField_ln2kpxpf') && !isNaN(Number(item.numberField_ln2kpxpf))) {
                WarehousingCost += Number(item.numberField_ln2kpxpf);
            }
            if (item.hasOwnProperty('numberField_ln2kpxpg') && !isNaN(Number(item.numberField_ln2kpxpg))) {
                ProductSubsidy += Number(item.numberField_ln2kpxpg);
            }
            if (item.hasOwnProperty('numberField_licip9px') && !isNaN(Number(item.numberField_licip9px))) {
                AdvertisingExpenses += Number(item.numberField_licip9px);
            }
            if (item.hasOwnProperty('numberField_licip9pz') && !isNaN(Number(item.numberField_licip9pz))) {
                ReplenishmentPrincipal += Number(item.numberField_licip9pz);
            }
            if (item.hasOwnProperty('numberField_licip9q0') && !isNaN(Number(item.numberField_licip9q0))) {
                ReplenishmentCost += Number(item.numberField_licip9q0);
            }
            if (item.hasOwnProperty('numberField_ln2kpxpp') && !isNaN(Number(item.numberField_ln2kpxpp))) {
                VINEEvaluationCost += Number(item.numberField_ln2kpxpp);
            }
            if (item.hasOwnProperty('numberField_licip9py') && !isNaN(Number(item.numberField_licip9py))) {
                OtherPromotions += Number(item.numberField_licip9py);
            }
            if (item.hasOwnProperty('numberField_licip9q3') && !isNaN(Number(item.numberField_licip9q3))) {
                DeliverrBudget += Number(item.numberField_licip9q3);
            }
            if (item.hasOwnProperty('numberField_licip9q4') && !isNaN(Number(item.numberField_licip9q4))) {
                OtherBudgets += Number(item.numberField_licip9q4);
            }
            if (item.hasOwnProperty('numberField_licip9q7') && !isNaN(Number(item.numberField_licip9q7))) {
                GrossProfitMarginTarget = GrossProfitTarget / SalesTarget;
            }
            if (item.hasOwnProperty('numberField_ln2kpxph') && !isNaN(Number(item.numberField_ln2kpxph))) {
                MarketingExpenses = AdvertisingExpenses + ReplenishmentPrincipal + VINEEvaluationCost + OtherPromotions;
            }
            if (item.hasOwnProperty('numberField_ln2kpxpi') && !isNaN(Number(item.numberField_ln2kpxpi))) {
                ProductCostRatio = ProductCost / SalesTarget;
            }
            if (item.hasOwnProperty('numberField_ln2kpxpj') && !isNaN(Number(item.numberField_ln2kpxpj))) {
                ShippingCostRatio = ShippingCost / SalesTarget;
            }
            if (item.hasOwnProperty('numberField_ln2kpxpk') && !isNaN(Number(item.numberField_ln2kpxpk))) {
                WarehousingCostRatio = WarehousingCost / SalesTarget;
            }
            if (item.hasOwnProperty('numberField_ln2kpxpl') && !isNaN(Number(item.numberField_ln2kpxpl))) {
                MarketingCostRatio = (AdvertisingExpenses + ReplenishmentPrincipal + VINEEvaluationCost + OtherPromotions) / SalesTarget;
            }

        }
    } else {
        console.error("value is not iterable");
    }

    // 添加新的"合计"项目到数组的开始
    value.unshift({
        textField_licip9pp: "合计",
        numberField_licip9pq: SalesTarget,
        numberField_licip9pr: GrossProfitTarget,
        numberField_ln2kpxpb: GrossProfitRedLine,
        numberField_ln2kpxpc: ProductSalesVolume,
        numberField_ln2kpxpd: ProductCost,
        numberField_ln2kpxpe: ShippingCost,
        numberField_ln2kpxpf: WarehousingCost,
        numberField_ln2kpxpg: ProductSubsidy,
        numberField_licip9px: AdvertisingExpenses,
        numberField_licip9pz: ReplenishmentPrincipal,
        numberField_licip9q0: ReplenishmentCost,
        numberField_ln2kpxpp: VINEEvaluationCost,
        numberField_licip9py: OtherPromotions,
        numberField_licip9q3: DeliverrBudget,
        numberField_licip9q4: OtherBudgets,
        numberField_licip9q7: GrossProfitMarginTarget,
        numberField_ln2kpxph: MarketingExpenses,
        numberField_ln2kpxpi: ProductCostRatio,
        numberField_ln2kpxpj: ShippingCostRatio,
        numberField_ln2kpxpk: WarehousingCostRatio,
        numberField_ln2kpxpl: MarketingCostRatio,
        textField_licip9q5: "详细备注见下方信息"
    });

    // 返回更新后的数据
    return value;
}