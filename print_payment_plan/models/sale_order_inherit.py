# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SalesOrder(models.Model):
    _inherit = 'sale.order'

    def print_payment_plan_report(self):
        return self.env.ref('print_payment_plan.payment_plan_report').report_action(self, config=False)
