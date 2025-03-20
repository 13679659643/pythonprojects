# -*- coding: utf-8 -*-
# @Time     : 2025/1/3 11:51
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : customs_declaration_responses.py
from typing import Union
from pydantic import BaseModel


# 报关商品数据模型
class CustomsDeclarationGoodsSchema(BaseModel):
    # 商品信息
    g_sn: Union[int, None] = 0  # 商品序号
    g_spu: Union[str, None] = 'None'  # 商品货号
    g_name_zh: Union[str, None] = 'None'  # 商品名称_zh
    g_name_en: Union[str, None] = 'None'  # 商品名称_en
    g_quantity: Union[int, str, None] = 0  # 商品数量
    g_price: Union[float, str, None] = 0  # 商品单价
    g_amount: Union[float, str, None] = 0  # 商品金额
    g_currency: Union[str, None] = '美元'  # 币种, '美元'
    g_gross_weight: Union[float, str, None] = 0  # 商品毛重
    g_net_weight: Union[float, str, None] = 0  # 商品净重
    g_unit: Union[str, None] = 'None'  # 商品单位, '双'
    g_place_of_origin: Union[str, None] = '中国'  # 产地, '中国'
    g_destination: Union[str, None] = '美国'  # 目的地, '美国'
    g_domestic_source: Union[str, None] = '泉州'  # 境内货源地, '泉州'
    g_hs_code: Union[str, None] = 'None'  # 商品HS编码
    g_specification_description: Union[str, None] = 'None'  # 规格描述
    g_brand: Union[str, None] = 'None'  # 商品品牌
    g_brand_description: Union[str, None] = 'None'  # 品牌描述


class CustomsDeclarationBaseSchema(BaseModel):
    """
    报关数据模型
    """
    is_same_company: Union[bool, None] = False
    # 形式发票 PROFORMA INVOICE
    pi_main_company_zh: Union[str, None] = 'None'  # 主体公司_zh
    pi_main_company_en: Union[str, None] = 'None'  # 主体公司_en
    pi_consignee: Union[str, None] = 'None'  # 买方
    pi_main_company_address_en: Union[str, None] = 'None'  # 主体地址_en
    pi_company: Union[str, None] = 'None'  # 卖方
    pi_contact: Union[str, None] = 'None'  # 联系人, 'Contact: 联系人'
    pi_address: Union[str, None] = 'None'  # 送达地址
    pi_email: Union[str, None] = 'None'  # 电子邮件
    pi_pl_no: Union[str, None] = 'None'  # 合同编号, 'PL No.: 合同编号
    pi_date: Union[str, None] = 'None'  # 合同日期, 'Date: 合同日期'
    pi_others: Union[str, None] = 'None'  # 其他预留信息
    # 销售合同 SALES CONTRACT
    sc_no: Union[str, None] = 'None'  # 合同编号
    sc_date: Union[str, None] = 'None'  # 合同日期
    sc_signed_at: Union[str, None] = 'None'  # 签订地点
    sc_buyer_company_zh: Union[str, None] = 'None'  # 买方公司_zh
    sc_buyer_company_en: Union[str, None] = 'None'  # 买方公司_en
    sc_buyer_address_zh: Union[str, None] = 'None'  # 买方地址_zh
    sc_buyer_address_en: Union[str, None] = 'None'  # 买方地址_en
    sc_seller_company_zh: Union[str, None] = 'None'  # 卖方公司_zh
    sc_seller_company_en: Union[str, None] = 'None'  # 卖方公司_en
    sc_seller_address_zh: Union[str, None] = 'None'  # 卖方地址_zh
    sc_seller_address_en: Union[str, None] = 'None'  # 卖方地址_en
    sc_place_of_origin_zh: Union[str, None] = '中国'  # 货件生产国_zh, '中国'
    sc_place_of_origin_en: Union[str, None] = 'China'  # 货件生产国_en, 'China'
    sc_point_of_shipment_zh: Union[str, None] = '厦门，中国'  # 装运地_zh, '厦门，中国'
    sc_point_of_shipment_en: Union[str, None] = 'Xiamen,China'  # 装运地_en, 'Xiamen,China'
    sc_destination_zh: Union[str, None] = '美国'  # 目的地_zh, '美国'
    sc_destination_en: Union[str, None] = 'American'  # 目的地_en, 'American'
    sc_contract_payment: Union[float, None] = 0  # 销售合同金额
    sc_place_of_delivery_zh: Union[str, None] = '厦门港口，中国'  # 交付地点, '厦门港口，中国'
    sc_place_of_delivery_en: Union[str, None] = 'Xiamen Port,China'  # 交付地点, 'Xiamen Port,China'
    sc_destination_address: Union[str, None] = 'None'  # 送达地址
    sc_others: Union[str, None] = 'None'  # 其他预留信息
    # 装箱单 PACKING LIST
    pl_main_company_en: Union[str, None] = 'None'  # 主体公司
    pl_consignee: Union[str, None] = 'None'  # 买方
    pl_company: Union[str, None] = 'None'  # 卖方
    pl_address: Union[str, None] = 'None'  # 送达地址
    pl_invoice_no: Union[str, None] = 'None'  # 发票号
    pl_date: Union[str, None] = 'None'  #
    pl_delivery_to: Union[str, None] = 'Xiamen'
    pl_others: Union[str, None] = 'None'  # 其他预留信息
    # 报关草单
    cd_domestic_shipper: Union[str, None] = 'None'  # 境内发货人
    cd_overseas_consignee: Union[str, None] = 'None'  # 境外收货人
    cd_production_and_sales_company: Union[str, None] = 'None'  # 生产销售公司
    cd_customs_code: Union[str, None] = 'None'  # 海关代码
    cd_protocol_no: Union[str, None] = 'None'  # 合同协议号
    cd_transport_mode: Union[str, None] = '水路运输'  # 运输方式, '水路运输
    cd_supervision_mode: Union[str, None] = 'None'  # 监管方式, '9810' or '一般贸易'
    cd_exemption_nature: Union[str, None] = '一般征税'  # 征免性质,   一般征税
    cd_transaction_mode: Union[str, None] = 'C&F'  # 成交方式,  C&F
    cd_trading_country_or_region: Union[str, None] = 'None'  # 贸易国（地区）
    cd_arrival_country_or_region: Union[str, None] = 'None'  # 运抵国（地区）
    cd_others: Union[str, None] = 'None'  # 其他预留信息
    # 货件信息
    shipment_ids: Union[str, None] = 'None'  # 货件id
    shipment_cartons: Union[int, str, None] = 0  # 货件件数（箱数）
    shipment_gross_weight: Union[float, str, None] = 0  # 货件毛重
    shipment_net_weight: Union[float, str, None] = 0  # 货件净重
    shipment_freight: Union[float, str, None] = 0  # 货件运费
    shipment_total_quantity: Union[int, str, None] = 0  # 总双数
    shipment_others: Union[str, None] = 'None'  # 其他预留信息
    # 商品信息列表
    goods_list: Union[list[CustomsDeclarationGoodsSchema], None] = None  # 商品列表
