# -*- coding: utf-8 -*-
# @Time     : 2025/1/6 17:50
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : sql.py


query_sql_customs_declaration_base_data = """
select ''                                                          as dt,
    if(count(distinct dftmcim.company_name_zh) = 1, 1, 0)       as is_same_company,                 # 是否为同一主体
       # 形式发票 PROFORMA INVOICE
       dftmcim.company_name_zh                                     as pi_main_company_zh,              # 主体公司_zh
       dftmcim.company_name_en                                     as pi_main_company_en,              # 主体公司_en
       case
           when dftmcim.supervision_mode = '9810' then 'Amazon FBA Warehouse'
           when dftmcim.supervision_mode = '一般贸易' then 'YUNJING INTERNATIONAL TRADING LIMITED'
           else '' end                                             as pi_consignee,                    # 买方
       dftmcim.address_en                                          as pi_main_company_address_en,      # 主体地址
       case
           when dftmcim.supervision_mode = '一般贸易' then 'YUNJING INTERNATIONAL TRADING LIMITED'
           when dftmcim.supervision_mode = '9810' then dftmcim.company_name_en
           else '' end                                             as pi_company,                      # 卖方
       ''                                                          as pi_contact,                      # 联系人
       concat(dgslcim.ship_to_address, ' ', dgslcim.ship_to_city, ' ', ship_to_province_code, ' ',
              dgslcim.ship_to_country, ' ', dgslcim.ship_to_country_code, ' ', dgslcim.ship_to_postal_code, ' ',
              '(', dgslcim.destination_fulfillment_center_id, ')') as pi_address,                      # 送达地址
       ''                                                          as pi_pl_no,                        # 合同编号
       ''                                                          as pi_date,                         # 合同日期
       ''                                                          as pi_others,                       # 其他预留信息
       # 销售合同
       ''                                                          as sc_no,                           # 'None'  # 合同编号
       ''                                                          as sc_date,                         # 'None'  # 合同日期
       ''                                                          as sc_signed_at,                    # 'None'  # 签订地点
       case
           when dftmcim.supervision_mode = '9810' then 'Amazon FBA Warehouse'
           when dftmcim.supervision_mode = '一般贸易' then 'YUNJING INTERNATIONAL TRADING LIMITED'
           else '' end                                             as sc_buyer_company_zh,             # 'None'  # 买方公司_zh
       case
           when dftmcim.supervision_mode = '9810' then 'Amazon FBA Warehouse'
           when dftmcim.supervision_mode = '一般贸易' then 'YUNJING INTERNATIONAL TRADING LIMITED'
           else '' end                                             as sc_buyer_company_en,             # 'None'  # 买方公司_en
       case
           when dftmcim.supervision_mode = '一般贸易' then '6/F MANULIFE PLACE 348 KWUNTONG RDKL'
           when dftmcim.supervision_mode = '9810' then concat(dgslcim.ship_to_address, ' ', dgslcim.ship_to_city, ' ',
                                                              ship_to_province_code, ' ', dgslcim.ship_to_country, ' ',
                                                              dgslcim.ship_to_country_code, ' ',
                                                              dgslcim.ship_to_postal_code, ' ',
                                                              '(', dgslcim.destination_fulfillment_center_id, ')')
           else '' end                                             as sc_buyer_address_zh,             # 'None'  # 买方地址_zh
       case
           when dftmcim.supervision_mode = '一般贸易' then '6/F MANULIFE PLACE 348 KWUNTONG RDKL'
           when dftmcim.supervision_mode = '9810' then concat(dgslcim.ship_to_address, ' ', dgslcim.ship_to_city, ' ',
                                                              ship_to_province_code, ' ', dgslcim.ship_to_country, ' ',
                                                              dgslcim.ship_to_country_code, ' ',
                                                              dgslcim.ship_to_postal_code, ' ',
                                                              '(', dgslcim.destination_fulfillment_center_id, ')')
           else '' end                                             as sc_buyer_address_en,             # 'None'  # 买方地址_en
       dftmcim.company_name_zh                                     as sc_seller_company_zh,            # 'None'  # 卖方公司_zh
       dftmcim.company_name_en                                     as sc_seller_company_en,            # 'None'  # 卖方公司_en
       dftmcim.address_zh                                          as sc_seller_address_zh,            # 'None'  # 卖方地址_zh
       dftmcim.address_en                                          as sc_seller_address_en,            # 'None'  # 卖方地址_en
       '中国'                                                      as sc_place_of_origin_zh,           # '中国'  # 货件生产国_zh, '中国'
       'China'                                                     as sc_place_of_origin_en,           # 'China'  # 货件生产国_en, 'China'
       '厦门，中国'                                                 as sc_point_of_shipment_zh,         # '厦门，中国'  # 装运地_zh, '厦门，中国'
       'Xiamen,China'                                              as sc_point_of_shipment_en,         # 'Xiamen,China'  # 装运地_en, 'Xiamen,China'
       '美国'                                                      as sc_destination_zh,               # '美国'  # 目的地_zh, '美国'
       'American'                                                  as sc_destination_en,               # 'American'  # 目的地_en, 'American'
       0                                                           as sc_contract_payment,             # 0  # 销售合同金额
       '厦门港口，中国'                                             as sc_place_of_delivery_zh,         # '厦门港口，中国'  # 交付地点, '厦门港口，中国'
       'Xiamen Port,China'                                         as sc_place_of_delivery_en,         # 'Xiamen Port,China'  # 交付地点, 'Xiamen Port,China'
       concat(dgslcim.ship_to_address, ' ', dgslcim.ship_to_city, ' ', ship_to_province_code, ' ',
              dgslcim.ship_to_country, ' ', dgslcim.ship_to_country_code, ' ', dgslcim.ship_to_postal_code, ' ',
              '(', dgslcim.destination_fulfillment_center_id, ')') as sc_destination_address,          # 'None'  # 送达地址
       ''                                                          as sc_others,                       # 'None'  # 其他预留信息
       # 装箱单 PACKING LIST
       dftmcim.company_name_en                                     as pl_main_company_en,           # 主体公司
       case
           when dftmcim.supervision_mode = '9810' then 'Amazon FBA Warehouse'
           when dftmcim.supervision_mode = '一般贸易' then 'YUNJING INTERNATIONAL TRADING LIMITED'
           else '' end                                             as pl_consignee,                    # 买方
       case
           when dftmcim.supervision_mode = '一般贸易' then 'YUNJING INTERNATIONAL TRADING LIMITED'
           when dftmcim.supervision_mode = '9810' then dftmcim.company_name_en
           else '' end                                             as pl_company,                      # 卖方
       concat(dgslcim.ship_to_address, ' ', dgslcim.ship_to_city, ' ', ship_to_province_code, ' ',
              dgslcim.ship_to_country, ' ', dgslcim.ship_to_country_code, ' ', dgslcim.ship_to_postal_code, ' ',
              '(', dgslcim.destination_fulfillment_center_id, ')') as pl_address,                      # 送达地址
       ''                                                          as pl_invoice_no,                   # 发票号
       ''                                                          as pl_date,                         #
       'Xiamen'                                                    as pl_delivery_to,
       ''                                                          as pl_others,                       # 其他预留信息
       # 报关草单
       dftmcim.company_name_zh                                     as cd_domestic_shipper,             # 境内发货人
       case
           when dftmcim.supervision_mode = '9810' then 'Amazon FBA Warehouse'
           when dftmcim.supervision_mode = '一般贸易' then 'YUNJING INTERNATIONAL TRADING LIMITED'
           else '' end                                             as cd_overseas_consignee,           # 海外收货人
       dftmcim.company_name_zh                                     as cd_production_and_sales_company, # 生产销售公司
       dftmcim.customs_code                                        as cd_customs_code,                 # 海关代码
       ''                                                          as cd_protocol_no,                  # 合同协议号
       '水路运输'                                                  as cd_transport_mode,               # 运输方式, '水路运输'
       dftmcim.supervision_mode                                    as cd_supervision_mode,             # 监管方式, '9810' or '一般贸易'
       '一般征税'                                                  as cd_exemption_nature,             # 征免性质,   一般征税
       dftmcim.transaction_mode                                    as cd_transaction_mode,             # 成交方式,  C&F
       case
           when dftmcim.supervision_mode = '9810' then '美国'
           when dftmcim.supervision_mode = '一般贸易' then '香港'
           else '' end                                             as cd_trading_country_or_region,    # 贸易国（地区）
       '美国'                                                      as cd_arrival_country_or_region,    # 运抵国（地区）
       ''                                                          as cd_others,                       # 其他预留信息
# 货件信息
       group_concat(dswlfdid.shipment_id)                          as shipment_ids,                    # 货件id
       sum(dswlfdid.total_qty)                                     as shipment_cartons,                # 货件件数（箱数）
       sum(dswmlttid.logistics_weight)                             as shipment_gross_weight,           # 货件毛重
       sum(dswmlttid.volume_weight)                                as shipment_net_weight,             # 货件净重
       0                                                           as shipment_freight,                # 货件运费
       sum(dswmlttid.shoes_even)                                   as shipment_total_quantity,         # 总双数
       ''                                                          as shipment_others                  # 其他预留信息
from dwm_prod.dwm_scg_wld_lx_fba_drawback_i_d dswlfdid # 退税货件主体
         left join dim_prod.dim_fc_tax_main_company_i_manual dftmcim # 退税主体维度表
                   on dswlfdid.drawback_name = dftmcim.company_sname
         left join dwm_prod.dwm_scg_wld_me_logistics_trace_table_i_d dswmlttid # 物流轨迹
                   on dswlfdid.shipment_id = dswmlttid.shipment_id
         left join ods_prod.ods_gsm_lx_fba_shipment_carton_i_h dgslcim # FBA货件详情
                   on dswlfdid.shipment_id = dgslcim.shipment_id
WHERE dswlfdid.shipment_id in ({shipment_ids})
group by dftmcim.company_name_zh;
"""

query_sql_customs_declaration_goods_data = """
select origin.*,
       row_number() over (order by origin.g_spu) as g_sn,           # 序号
       g_quantity * g_price                      as g_amount,       # 商品金额
       0                                         as g_gross_weight, # 商品毛重
       0                                         as g_net_weight    # 商品净重
from (select
          # 商品信息
          ifnull(dglpmad.iteration_spu, '')     as g_spu,                       # 商品货号
          ifnull(dftdeim.product_name_zh, '')   as g_name_zh,                   # 商品名称_zh
          ifnull(dftdeim.product_name_en, '')   as g_name_en,                   # 商品名称_en
          sum(oglssodid.num)                    as g_quantity,                  # 商品数量
          0                                     as g_price,                     # 商品单价
          '美元'                                as g_currency,                  # 币种, '美元'
          '双'                                  as g_unit,                      # 商品单位, '双'
          '中国'                                as g_place_of_origin,           # 产地, '中国'
          '美国'                                as g_destination,               # 目的地, '美国'
          '泉州'                                as g_domestic_source,           # 境内货源地, '泉州'
          ifnull(dftdeim.hs_code, '')           as g_hs_code,                   # 商品HS编码
          ifnull(dftdeim.product_specification_description, '')             as g_specification_description, # 规格描述
          ifnull(dftdeim.brand, '') as g_brand,                     # 商品品牌
          ifnull(dftdeim.brand_description, '') as g_brand_description          # 品牌描述
      from dwm_prod.dwm_scg_wld_lx_fba_drawback_i_d dswlfdid # 退税货件主体
               left join ods_prod.ods_gsm_lx_shipment_ship_order_detail_i_d oglssodid # 发货单明细
                         on dswlfdid.shipment_id = oglssodid.shipment_id
               left join dim_prod.dim_gsm_lx_product_manage_a_d dglpmad # 商品管理
                         on oglssodid.sku = dglpmad.original_local_sku
               left join dim_prod.dim_fc_tax_declaration_elements_i_manual dftdeim # 商品申报要素
                         on dglpmad.iteration_spu = dftdeim.spu
      where dswlfdid.shipment_id in ({shipment_ids})
      group by dglpmad.iteration_spu) origin
"""
