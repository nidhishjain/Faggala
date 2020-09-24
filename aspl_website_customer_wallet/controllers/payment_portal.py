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

from odoo import http
from odoo.http import request
from datetime import date
from odoo.addons.account_payment.controllers.payment import PaymentPortal
from odoo.addons.payment.controllers.portal import PaymentProcessing


class PaymentPortal(PaymentPortal):

    @http.route('/invoice/pay/<int:invoice_id>/form_tx', type='json', auth="public", website=True)
    def invoice_pay_form(self, acquirer_id, invoice_id, save_token=False,
                         access_token=None, **kwargs):
        res = super(PaymentPortal, self).invoice_pay_form(acquirer_id, invoice_id,
                                                          save_token=save_token,
                                                          access_token=access_token)
        tx_ids_list = PaymentProcessing.get_payment_transaction_ids()
        payment_transaction_ids = request.env['payment.transaction'].sudo().search([
            ('id', 'in', list(tx_ids_list)),
        ]).filtered(lambda rec: invoice_id in rec.invoice_ids.ids)
        tx = payment_transaction_ids and payment_transaction_ids[0]
        if tx:
            if tx.acquirer_id and tx.acquirer_id.wallet_acquirer:
                request.env['customer.wallet'].sudo().create({
                    'transaction_type': 'debit',
                    'partner_id': tx.partner_id.id,
                    'amount': -float(tx.amount),
                    'currency_id': int(tx.currency_id.id),
                    'invoice_id': invoice_id,
                    'reference': tx.reference,
                    'date': date.today(),
                })
            elif tx.acquirer_id and not tx.acquirer_id.wallet_acquirer and \
                    tx.invoice_ids.partial_pay:
                request.env['customer.wallet'].sudo().create({
                    'transaction_type': 'debit',
                    'partner_id': tx.partner_id.id,
                    'amount': -float(tx.invoice_ids.partial_pay),
                    'currency_id': int(tx.currency_id.id),
                    'invoice_id': invoice_id,
                    'reference': str(tx.reference) + '' + 'Wallet',
                    'date': date.today(),
                })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
