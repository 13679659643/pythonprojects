# _*_ coding: utf-8 _*_
# @Time : 2025/1/13
# @Author : 杨洋
# @Email ： yangyang@doocn.com
# @File : crawler-temu-seller-kuajingmaihuo-data
# @Desc :
from dataclasses import dataclass


@dataclass
class OdsBD27OnSaleSPU:
    __tablename__ = 'dim_prod.dim_gsm_bd27_on_sale_spu_i_manual'
    spu: str
    status_text: str
    channel: str
