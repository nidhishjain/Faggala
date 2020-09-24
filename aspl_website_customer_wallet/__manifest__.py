# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

{
    'name': 'Website Customer Wallet',
    'version': '13.0.1.0.0',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'summary': 'Customer Website Wallet.',
    'sequence': 1,
    'website': 'http://www.acespritech.com',
    'category': 'Website',
    'price': 25.00,
    'currency': 'EUR',
    'depends': ['base', 'website_sale', 'account_payment', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'data/payment_acquirer_data.xml',
        'data/mail_template_data.xml',
        'data/wallet_transaction_data.xml',
        'views/res_config_template.xml',
        'views/customer_wallet_template.xml',
        'views/customer_wallet_view.xml',
        'views/payment_template.xml',
        'views/res_partner_view.xml',
        'views/payment_acquirer_view.xml',
        'views/payment_transaction_view.xml',
        'views/website_template.xml'
        ],
    'images': ['static/description/odoo13_13_website_shop_payment_configuration_remaining_wallet.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': '_set_email',
}
