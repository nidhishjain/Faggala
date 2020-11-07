# -*-	coding:	utf-8	-*-
from odoo import models, api, fields, _


class Installment(models.Model):
    _name = "sale.maintenance"
    _description = "Maintenance"
    _inherit = "mail.thread"

    sale_id_main = fields.Many2one(comodel_name="sale.order", required=True, ondelete='cascade')
    maintenance_date = fields.Date(copy=False)
    maintenance_amount = fields.Float()
    status = fields.Selection(string="Payment Type", selection=[('paid', 'Paid'),
                                                                ('not_paid', 'Not Paid')],
                              copy=False, default='not_paid')
    name = fields.Char(string="Seq", required=True, copy=False, default='New')
