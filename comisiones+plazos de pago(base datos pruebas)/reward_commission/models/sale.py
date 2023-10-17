# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime
class SaleOrder(models.Model):
    _inherit = "sale.order"

    hair_dresser_id = fields.Many2one('res.partner','Hairdresser')

    def create_account_move(self,partner_id,commission):
        commission_prd = self.env.ref('reward_commission.product_commission_product_template')

        if partner_id and commission:
            self.env['account.move'].sudo().create({
                'partner_id': partner_id.id,
                'type':'in_invoice',
                'invoice_line_ids': [
                    (0, None, {
                        'product_id': commission_prd.id,
                        'quantity': 1,
                        # 'account_id': self.env.ref('l10n_es.1_account_common_4100'),
                        'price_unit': self.amount_untaxed * (commission / 100),
                        'product_uom_id':1,
                        'tax_ids': [(6, 0, commission_prd.supplier_taxes_id.ids)]
                        })
                ],
            })


    def _write(self, values):

        res = super(SaleOrder, self)._write(values)

        for saleorder in self:
            if saleorder.invoice_status == 'invoiced' and 'invoice_status' in values: #already sold . start to create reward_commission

                if saleorder.partner_id.partner_type == 'hairdresser': #hairdresser
                    distributor_id = saleorder.partner_id.distributor_id
                    commission = 0
                    commission = 7 + distributor_id.certification_commission
                    saleorder.create_account_move(distributor_id,commission)


                if saleorder.partner_id.partner_type != 'hairdresser' and  saleorder.partner_id.partner_type != 'distributor':

                    if saleorder.hair_dresser_id:
                        hairdresser_id = saleorder.hair_dresser_id
                        commission = 0
                        commission = 3 + hairdresser_id.certification_commission
                        saleorder.create_account_move(hairdresser_id,commission)


                        if hairdresser_id.distributor_id:
                            distributor_id = hairdresser_id.distributor_id
                            commission = 0
                            commission = 2 + distributor_id.certification_commission
                            saleorder.create_account_move(distributor_id,commission)

        return res
