# -*- coding: utf-8 -*-
{
    'name': "Trend Real Estate Installments Plan",
    'summary': "Trend Real Estate Installments Plan",
    'description': """
        This module calculate installments in quotations
          
     """,
    'author': "Trend Development Team",
    'category': 'Sales',
    'depends': ['base', 'trend_realestate_unit'],
    'data': [
        'security/ir.model.access.csv',
        'views/installment_seq_view.xml',
        'views/maintenance_seq_view.xml',
        'views/sale_order_inherit_view.xml',

    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
