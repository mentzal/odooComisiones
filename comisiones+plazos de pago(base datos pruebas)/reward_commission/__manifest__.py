# -*- coding: utf-8 -*-

{
    'name': 'Reward Commission',
    'version': '1.6',
    'summary': 'Reward to resellers and hairdressers by commisions',
    'category': 'Tools',
    'depends': [
        'website_sale',
        'survey',
        'base_geolocalize',
    ],
    'data': [
        'data/product.xml',
        'data/geo_localize_partner.xml',

        # backend
        'views/backend/res_partner_form.xml',
        'views/backend/survey_view_input.xml',
        'views/backend/res_config.xml',
        'views/backend/sale_order_form_view.xml',

        # frontend
        'views/frontend/assets.xml',
        'views/frontend/payment.xml',
        'views/frontend/portal.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
