# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hair_dresser_commission = fields.Float(string='Hairdressers commission', default=7, readonly=False)
    distributor_to_end_user_commission = fields.Float(string='Distributor to end user commission', default=2, readonly=False)
    distributor_to_hairdresser_commission = fields.Float(string='Distributor to hairdressers commission', default=3, readonly=False)
