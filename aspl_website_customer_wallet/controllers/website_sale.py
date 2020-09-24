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

from odoo import http, _
from odoo.http import request
from datetime import date
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):

    @http.route(['/shop/payment/transaction/',
                 '/shop/payment/transaction/<int:so_id>',
                 '/shop/payment/transaction/<int:so_id>/<string:access_token>'], type='json', auth="public",
                website=True)
    def payment_transaction(self, acquirer_id, save_token=False, so_id=None, access_token=None, token=None, **kwargs):
        res = super(WebsiteSale, self).payment_transaction(acquirer_id, save_token=save_token, so_id=so_id,
                                                           access_token=access_token, token=token, )

        last_tx_id = request.session.get('__website_sale_last_tx_id')
        if last_tx_id:
            tx = request.env['payment.transaction'].browse(last_tx_id).sudo().exists()
            if tx.acquirer_id and tx.acquirer_id.wallet_acquirer:
                wallet_tx = request.env['customer.wallet'].sudo().create({
                    'transaction_type': 'debit',
                    'partner_id': tx.partner_id.id,
                    'amount': -float(tx.amount),
                    'currency_id': int(tx.currency_id.id),
                    'order_id': tx.sale_order_ids.id,
                    'reference': tx.reference,
                    'date': date.today(),
                })
            elif tx.acquirer_id and not tx.acquirer_id.wallet_acquirer and tx.sale_order_ids.partial_pay_amount:
                wallet_tx = request.env['customer.wallet'].sudo().create({
                    'transaction_type': 'debit',
                    'partner_id': tx.partner_id.id,
                    'amount': -float(tx.sale_order_ids.partial_pay_amount),
                    'currency_id': int(tx.currency_id.id),
                    'order_id': tx.sale_order_ids.id,
                    'reference': str(tx.reference) + '' + 'Wallet',
                    'date': date.today(),
                })
        return res

    @http.route('/shop/payment/validate', type='http', auth="public", website=True)
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        if sale_order_id is None:
            order = request.website.sale_get_order()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')

        if transaction_id:
            tx = request.env['payment.transaction'].sudo().browse(transaction_id)
            assert tx in order.transaction_ids()
        elif order:
            tx = order.get_portal_last_transaction()
        else:
            tx = None
        res = super(WebsiteSale, self).payment_validate(transaction_id=transaction_id, sale_order_id=sale_order_id)
        if tx:
            wallet_transaction_id = request.env['customer.wallet'].search([('reference', '=', tx.reference),
                                                                           ('partner_id', '=', tx.partner_id.id),
                                                                           ('transaction_type', '=', 'debit')])
            if wallet_transaction_id:
                    wallet_transaction_id.update({
                        'state': tx.state
                    })
            # template = request.env.ref('aspl_website_customer_wallet.used_email_customer_template')
            template = request.env['res.config.settings'].sudo().search([], order='id desc', limit=1)
            if template and template.used_wallet_template_id and wallet_transaction_id:
                template.used_wallet_template_id.send_mail(wallet_transaction_id.id, True,
                                   email_values={'email_to': wallet_transaction_id.partner_id.email})
        if tx and tx.sale_order_ids and tx.sale_order_ids.partial_pay_amount:
            wallet_transaction_id1 = request.env['customer.wallet'].search([('reference', '=', str(tx.reference) + '' + 'Wallet'),
                                                                           ('partner_id', '=', tx.partner_id.id),
                                                                           ('transaction_type', '=', 'debit')])
            if wallet_transaction_id1:
                wallet_transaction_id1.update({
                    'state': tx.state
                })
                # template = request.env.ref('aspl_website_customer_wallet.used_email_customer_template')
                template = request.env['res.config.settings'].sudo().search([], order='id desc', limit=1)
                if template and template.used_wallet_template_id and wallet_transaction_id1:
                    template.used_wallet_template_id.send_mail(wallet_transaction_id1.id, True,
                                       email_values={'email_to': wallet_transaction_id1.partner_id.email})
            if tx and tx.state == 'done' and wallet_transaction_id1:
                tx1 = request.env['payment.transaction'].sudo().search([('reference', '=', str(tx.reference) + '' + 'Wallet'),
                                                                        ('partner_id', '=', tx.partner_id.id),
                                                                        ('sale_order_ids', '=', wallet_transaction_id1.order_id.id),
                                                                        ('acquirer_id', '=', request.env['payment.acquirer'].search([('wallet_acquirer', '=', True)], limit=1).id)]),
                if tx1:
                    tx1[0].state = tx.state
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

