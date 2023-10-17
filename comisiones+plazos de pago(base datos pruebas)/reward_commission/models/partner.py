# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.http import request
from datetime import date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta

DISTRIBUTOR_V = .5
HAIRDRESSE_V = 1


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    partner_type = fields.Selection(selection=[
        ('distributor', 'Distributor'),
        ('hairdresser', 'Hairdresser')], string='Type')

    distributor_id = fields.Many2one('res.partner', 'Distributor')
    certification_commission = fields.Float(compute='_compute_certification_commission', string='certification commission %')
    total_commission = fields.Float(compute='_compute_total_certification', string='Total Commission')
    
    

    def _compute_total_certification(self):
        commission_product = self.env.ref('reward_commission.product_commission_product_template')
        account_moves_ids = self.env['account.move'].search([('partner_id', '=', self.id), ('type', 'not in', ('out_invoice', 'out_refund', 'out_receipt')), ('invoice_payment_state', '!=', 'paid')])
        total = 0
        for account_move in account_moves_ids:
            for invoices_line_id in account_move.invoice_line_ids:
                if invoices_line_id.product_id == commission_product:
                    total = total + invoices_line_id.price_total

        self.total_commission = total

    @api.depends('distributor_id')
    def _compute_certification_commission(self):
        if self.partner_type:
            survey_user_input = request.env['survey.user_input']
            date_range = (date.today() - relativedelta(years=1)).strftime(DEFAULT_SERVER_DATE_FORMAT)
            certifications = survey_user_input.search([('partner_id', '=', self.id), ('quizz_passed', '=', 1), ('date_completed', '>', date_range)])
            if len(certifications) > 0:
                if self.partner_type == 'distributor':
                    self.certification_commission = DISTRIBUTOR_V * len(certifications)

                if self.partner_type == 'hairdresser':
                    self.certification_commission = HAIRDRESSE_V * len(certifications)
            else:
                self.certification_commission = None
        else:
            self.certification_commission = None

    def _geo_localize_all_partners(self):
        partners = self.search([])
        for partner in partners:
            if not partner.date_localization:
                partner.geo_localize()
    @api.model
    def _geo_localize(self, street='', zip='', city='', state='', country=''):
        geo_obj = self.env['base.geocoder']
        search = geo_obj.geo_query_address(street=street, zip=zip, city=city, state=state, country=country)
        result = geo_obj.geo_find(search, force_country=country)
        if result is None:
            search = geo_obj.geo_query_address(zip=zip, city=city, state=state, country=country)
            result = geo_obj.geo_find(search, force_country=country)
        if result is None:
            search = geo_obj.geo_query_address(city=city, state=state, country=country)
            result = geo_obj.geo_find(search, force_country=country)
        return result
