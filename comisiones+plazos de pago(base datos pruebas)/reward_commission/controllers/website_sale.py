from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleExtend(WebsiteSale):

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        res = super(WebsiteSaleExtend, self).address(**kw)
        if 'countries' in res.qcontext:
            countries = res.qcontext['countries'].filtered(lambda x: x.code is not  False)
            res.qcontext.update({'countries':countries})
        return res
