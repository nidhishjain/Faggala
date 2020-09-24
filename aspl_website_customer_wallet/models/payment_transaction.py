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
import logging
import json
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    wallet_transaction = fields.Boolean(string='Wallet Transaction')

    def form_feedback(self, data, acquirer_name):
        tx = None
        tx_find_method_name = '_%s_form_get_tx_from_data' % acquirer_name
        if hasattr(self, tx_find_method_name):
            tx = getattr(self, tx_find_method_name)(data)
        res = super(PaymentTransaction, self).form_feedback(data, acquirer_name)

        if tx:
            wallet_transaction_id = self.env['customer.wallet'].\
                search([('reference', '=', tx.reference),
                        ('partner_id', '=', tx.partner_id.id),
                        ('transaction_type', '=', 'debit')])
            if wallet_transaction_id:
                wallet_transaction_id.update({
                    'state': tx.state
                })
        return res

    def _transfer_form_validate(self, data):
        if self.acquirer_id.provider == 'transfer' and self.acquirer_id.wallet_acquirer:
            _logger.info('Validated Wallet payment for tx %s: set as done' % (self.reference))
            self._set_transaction_done()
            return True
        else:
            return super(PaymentTransaction, self)._transfer_form_validate(data)


    def _reconcile_after_transaction_done(self):
        for rec in self:
            if rec.acquirer_id.provider == 'transfer' and rec.acquirer_id.wallet_acquirer:
                sales_orders = rec.mapped('sale_order_ids').\
                    filtered(lambda so: so.state in ('draft', 'sent'))
                for so in sales_orders:
                    so.with_context(send_email=True).action_confirm()
                rec._invoice_sale_orders()

                invoices = rec.mapped('invoice_ids').filtered(lambda inv: inv.state == 'draft')
                # invoices.action_invoice_open()
                invoices.action_post()
                invoices |= rec.mapped('invoice_ids').filtered(lambda inv: inv.state == 'posted')
                for inv in invoices:
                    if inv.invoice_has_outstanding:
                        outstanding_info = json.loads(inv.invoice_outstanding_credits_debits_widget)
                        if 'content' in outstanding_info:
                            for item in outstanding_info['content']:
                                credit_aml_id = item.get('id', False)
                                if credit_aml_id and inv.state == 'posted':
                                    inv.js_assign_outstanding_line(credit_aml_id)
                    # if inv.payment_ids:
                    #     inv.payment_ids.update({'payment_transaction_id': rec})

                if self.env['ir.config_parameter'].sudo().get_param('sale.automatic_invoice'):
                    default_template = self.env['ir.config_parameter'].\
                        sudo().get_param('sale.default_email_template')
                    if default_template:
                        ctx_company = {
                            'company_id': rec.acquirer_id.company_id.id,
                            'force_company': rec.acquirer_id.company_id.id,
                            'mark_invoice_as_sent': True,
                        }
                        if rec.sale_order_ids:
                            rec = rec.with_context(ctx_company)
                            for invoice in rec.invoice_ids:
                                invoice.message_post_with_template(int(default_template), email_layout_xmlid="mail.mail_notification_paynow")
            elif rec.acquirer_id.provider != 'transfer' and not rec.acquirer_id.wallet_acquirer:
                super(PaymentTransaction, self)._reconcile_after_transaction_done()
                invoices = rec.mapped('invoice_ids').filtered(lambda inv: inv.state == 'draft')
                # invoices.action_invoice_open()
                invoices.action_post()
                invoices |= rec.mapped('invoice_ids').filtered(lambda inv: inv.state == 'posted')
                for inv in invoices:
                    if inv.invoice_has_outstanding:
                        outstanding_info = json.loads(inv.invoice_outstanding_credits_debits_widget)
                        if 'content' in outstanding_info:
                            for item in outstanding_info['content']:
                                credit_aml_id = item.get('id', False)
                                if credit_aml_id and inv.state == 'posted':
                                    inv.js_assign_outstanding_line(credit_aml_id)
                    # if inv.payment_ids:
                    #     inv.payment_ids.update({'payment_transaction_id': rec})


    def render_sale_button(self, order, submit_txt=None, render_values=None):
        values = {
            'partner_id': order.partner_id.id,
        }
        if render_values:
            values.update(render_values)
        # Not very elegant to do that here but no choice regarding the design.
        self._log_payment_transaction_sent()
        amount = order.amount_total - order.partial_pay_amount
        return self.acquirer_id.with_context(submit_class='btn btn-primary',
                                             submit_txt=submit_txt or _('Pay Now')).sudo().render(
            self.reference,
            amount or order.amount_total,
            order.pricelist_id.currency_id.id,
            values=values,
        )

    def render_invoice_button(self, invoice, submit_txt=None, render_values=None):
        values = {
            'partner_id': invoice.partner_id.id,
        }
        if render_values:
            values.update(render_values)
        amount = invoice.amount_residual_signed - invoice.partial_pay
        return self.acquirer_id.with_context(submit_class='btn btn-primary',
                                             submit_txt=submit_txt or _('Pay Now')).sudo().render(
            self.reference,
            amount or invoice.amount_residual_signed,
            invoice.currency_id.id,
            values=values,
        )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
