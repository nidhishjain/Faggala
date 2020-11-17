# -*-	coding:	utf-8	-*-
import logging
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class SaleInstallment(models.Model):
    _name = "sale.installment"
    _description = "Installment"
    _inherit = "mail.thread"

    sale_id = fields.Many2one(comodel_name="sale.order", required=True, ondelete='cascade')
    installment_date = fields.Date(copy=False)
    installment_amount = fields.Float()
    status = fields.Selection(string="Payment Status", selection=[('paid', 'Paid'),
                                                                ('not_paid', 'Not Paid')],
                              copy=False, default='not_paid')
    name = fields.Integer(string="Seq", required=True, copy=False, default='0')

    installment_type = fields.Selection(string="Installment Type", selection=[('regular', 'Regular Installment'),
                                                                              ('delivery', 'Delivery Amount'),
                                                                              ('deposit', 'Deposit Amount'),
                                                                              ('contract_signing',
                                                                               'Contract Signing Amount'),
                                                                              ], )
