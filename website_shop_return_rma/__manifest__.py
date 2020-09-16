# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Website RMA - Return Orders Management",
    'price': 29.0,
    'version': '1.3.9',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This module allow your customer to create return RMA order and management of RMA.""",
    'description': """
Website Shop Return RMA
RMA
website rma
rma
RETURN MERCHANDISE AUTHORIZATION
Generate RMA
return merchandise authorization
website return merchandise authorization
View Of RMA Generated
List Of RMA(s) Created
my account rma
portal rma
customer rma
vendor rma
client rma
shop rma
ecommerce rma
customer return merchandise authorization
client return merchandise authorization
shop return merchandise authorization
ecommerce return merchandise authorization
portal return merchandise authorization
return order process
return order management
return order customer
customer returns
product return
website returns
website shop return
website ecommerce return
shop return odoo
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url' : 'https://youtu.be/eFu00LkVnjE', #'https://www.youtube.com/watch?v=Kiy-6podFRE&feature=youtu.be',
    'category' : 'Website',
    'depends': [
                'uom',
                'stock',
                'delivery',
#                'website_portal',
                'portal',
                'website_sale',
                'sale',
                ],
    'data':[
        'security/ir.model.access.csv',
        'security/rma_security.xml',
        'data/rma_sequence.xml',
        'views/website_portal_sale_templates.xml',
        'views/return_rma_view.xml',
        'views/saleorder_view.xml',
        'report/return_report.xml',
        'views/stock_picking_view.xml',
        'views/res_partner_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
