# -*- coding: utf-8 -*-
# @Time    : 2024/9/4 17:35
# @Author  : Night
# @File    : data_processing.py
# @Description:
from digiCore.db.tidb.core import TiDBDao


class DataProcessing:
    def __init__(self):
        self.tidb = TiDBDao('192.168.0.200')

    def get_customs_code(self):
        """
        海关编码获取
        :return:
        """
        sql = """
        SELECT original_spu,customs_code FROM dim_prod.dim_gsm_yida_product_customs_code_i_manual
        """
        original_data = self.tidb.query_list(sql)
        form_dict = {row['original_spu']: row['customs_code'] for row in original_data}
        return form_dict

    def get_fba_shipment_packed(self):
        """
        获取已发货后各个装箱 箱数
        dwd_scg_wld_lx_fba_shipment_box_detail_a_d 发货箱数
        dwd_scg_wld_lx_fba_shipment_box_detail_item_i_d  发货箱数详情信息

        货件详情
        ods_gsm_lx_fba_shipment_carton_i_h
        :return:
        """
        fba_sql = f"""
                SELECT fba_ship.shipment_id,
       fba_ship.address1,
       fba_ship.address2,
       fba_ship.ads,
       fba_ship.destination_fulfillment_center_id as fba_number,
       fba_ship.partner_trans_country_code        as country,
       dgsiim.country                             as zh_country,
       dgsiim.region,
       create_date,
       dgsiim.store_name,
       username,
       fba_ship.last_success_box_count,
       invoice_tax.vat,
       invoice_tax.eori,
       logistic.logistics_channel,
       logistic.declaration_type,
       logistic.clearance_type,
       logistic.logistics_provider_name
    FROM (SELECT name                                                    as address1,
             address1                                                as address2,
             CONCAT(ship_to_name, ",", ship_to_address, ",", ship_to_country, ",", ship_to_city, ",",
                    ship_to_province_code, ",", ship_to_postal_code) as ads,
             destination_fulfillment_center_id,
             partner_trans_country_code,
             shipment_id,
             create_date,
             seller_name,
             username,
             last_success_box_count,
             sids                                                    as sid
      FROM ods_prod.ods_gsm_lx_fba_shipment_carton_i_h
      WHERE shipment_id = '{self.shipment_id}') fba_ship
         LEFT JOIN (SELECT a.store_name, a.sid, a.country, a.region
                    FROM dim_prod.dim_gsm_me_store_info_i_manual a
                             JOIN (SELECT sid, MAX(version) as max_version
                                   FROM dim_prod.dim_gsm_me_store_info_i_manual
                                   GROUP BY sid) b ON a.sid = b.sid AND a.version = b.max_version) dgsiim
                   ON fba_ship.sid = dgsiim.sid
         LEFT JOIN dim_prod.dim_gsm_yida_invoice_tax_trade_numbers_i_manual invoice_tax
                   ON dgsiim.store_name = invoice_tax.store
         LEFT JOIN (select ods.shipment_id,
                           ods.logistics_channel,
                           '客户自主报关' as declaration_type,
                           case
                               when instr(delivery.remark, 'DCEU') > 1 and delivery.logistics_channel = '空运'
                                   then '递延PVA'
                               when instr(delivery.remark, 'DCEU') > 1 and delivery.logistics_channel != '空运'
                                   then '双清包税'
                               when ods.country = '英国' then '递延PVA'
                               else '双清包税'
                               end        as clearance_type,
                           ods.logistics_provider_name
                    from (select shipment_id, remark, logistics_channel, logistics_provider
                          from ods_prod.ods_scg_wld_me_shipment_delivery_record_i_h) as delivery
                             left join (select shipment_id, logistics_provider_name, logistics_channel, country
                                        from ods_prod.ods_scg_wld_logistics_provider_quotation_i_d) as ods
                                       on delivery.shipment_id = ods.shipment_id
                    WHERE delivery.shipment_id = '{self.shipment_id}'
                      and instr(ods.logistics_provider_name, delivery.logistics_provider) > 0) logistic
                   ON fba_ship.shipment_id = logistic.shipment_id
                """
        execute_data = self.tidb.query_one(fba_sql)
        return execute_data

    def get_box_list(self):
        """
        获取装箱
        :return:
        """
        box_sql = f"""
        select box_detail.shipment_id,
               dgsiim.store_name,
               dgsiim.sid,
               trim(substring_index(product_info.category, '-', -1)) as category,
               product_info.original_spu_color,
               product_info.brand,
               product_info.region,
               product_info.country,
               product_info.original_spu,
               product_info.original_color,
               box_id,
               length,
               width,
               height,
               weight,
               box_detail.msku,
               yd_sale_lk.sale_link,
               num
        from (SELECT shipment_id,
             box_id,
             length,
             width,
             height,
             weight,
             msku,
             num
        FROM dwd_prod.dwd_scg_wld_lx_fba_shipment_box_detail_item_i_d
        WHERE shipment_id = '{self.shipment_id}') box_detail
          left join dwd_prod.dwd_scg_wld_lx_fba_shipment_box_detail_a_d box
                   on box_detail.shipment_id = box.shipment_id
          left join (SELECT a.store_name, a.sid, a.country
                    FROM dim_prod.dim_gsm_me_store_info_i_manual a
                             JOIN (SELECT sid, MAX(version) as max_version
                                   FROM dim_prod.dim_gsm_me_store_info_i_manual
                                   GROUP BY sid) b ON a.sid = b.sid AND a.version = b.max_version) dgsiim
                   on box.sids = dgsiim.sid
          left join dim_prod.dim_cd_prd_lx_product_info_a_h product_info
                   on box_detail.msku = product_info.msku and box.sids = product_info.store_id
          left join dim_prod.dim_gsm_yida_invoice_sale_link_i_manual yd_sale_lk
                   on product_info.brand = yd_sale_lk.brand and dgsiim.store_name = yd_sale_lk.store
           ORDER BY CAST(box_id AS UNSIGNED)
        """
        execute_data = self.tidb.query_list(box_sql)
        return execute_data

    def get_declaration_info(self, shipment_id):
        sql = f"""
        select
    ods.logistics_channel,
    '客户自主报关'                              as declaration_type,
       case
           when instr(delivery.remark, 'DCEU') > 1 and delivery.logistics_channel = '空运' then '递延PVA'
           when instr(delivery.remark, 'DCEU') > 1 and delivery.logistics_channel != '空运' then '双清包税'
           when ods.country = '英国' then '递延PVA'
           else '双清包税'
           end                                                                                  as clearance_type,
	ods.logistics_provider_name
from
    (select shipment_id,remark,logistics_channel,logistics_provider from ods_prod.ods_scg_wld_me_shipment_delivery_record_i_h) as delivery
         left join (select shipment_id, logistics_provider_name, logistics_channel, country
                    from ods_prod.ods_scg_wld_logistics_provider_quotation_i_d) as ods
                   on delivery.shipment_id = ods.shipment_id
WHERE delivery.shipment_id = '{shipment_id}' and instr(ods.logistics_provider_name,delivery.logistics_provider) > 0
        """
        execute_data = self.tidb.query_one(sql)
        return execute_data

    def get_store_eori(self, store):
        sql = f"""
        SELECT eori FROM dim_prod.dim_gsm_yida_invoice_tax_trade_numbers_i_manual WHERE store = '{store}'
        """
        original_data = self.tidb.query_one(sql)
        return original_data['eori']

    def main(self):
        pass


if __name__ == "__main__":
    dp = DataProcessing()
    dp.main()
