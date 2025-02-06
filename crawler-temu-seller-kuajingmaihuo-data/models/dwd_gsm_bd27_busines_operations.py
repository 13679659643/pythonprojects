# _*_ coding: utf-8 _*_
# @Time : 2025/1/6
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : crawler-temu-seller-kuajingmaihuo-data
# @Desc :

from dataclasses import dataclass


@dataclass
class OdsBD27BusinesOperations:
    __tablename__ = 'ods_prod.ods_gsm_bd27_busines_operations_i_manual'
    dt: str
    platform: str
    store_name: str
    spu: str
    category: str
    activity_type: str
    registration_time: str
    start_time: str
    end_time: str
    registration_qty: str
    declared_price: str
    cost_price: str
    activity_manager: str
    goods_cost: str
    shipping_cost: str
    delivery_fee: str
    return_exchange_cost: str
    storage_cost: str
    other_fees: str
    predicted_profit: str
