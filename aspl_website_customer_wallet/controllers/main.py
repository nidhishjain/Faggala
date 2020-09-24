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

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.http import request, route, Response
from datetime import date
from odoo.osv import expression
from odoo.http import request
from odoo import http, _
import json
from datetime import datetime
from odoo.addons.website_form.controllers.main import WebsiteForm


class MyWallet(WebsiteSale):

    @http.route(['/login/wallet'], type="http", auth="user", website=True)
    def logging_wallet(self, **post):
        return request.render('aspl_website_customer_wallet.customer_wallet_logging')

    @http.route(['/my/wallet'], type="http", auth="public", website=True)
    def my_wallet(self, **kw):
        pin = kw.get('pin')
        user = request.env.user
        partner_id = request.env.user.partner_id
        if user.partner_id.customer_password and pin != user.partner_id.customer_password:
            return request.render('aspl_website_customer_wallet.customer_wallet_logging',
                                  {'error': '1'})

        if not user.partner_id.customer_password:
            user.partner_id.write({'customer_password': pin})
        currency = request.env.user.partner_id.currency_id
        vals = {'partner': partner_id, 'name': user.name, 'image': user.image_1920,
                'currency': currency}
        return request.render('aspl_website_customer_wallet.customer_wallet', vals)

    @http.route(['/change/pin'], type="json", auth="public", website=True)
    def change_pin(self, **kw):
        if kw.get('data') == 'password':
            user = request.env.user
            partner_id = request.env.user.partner_id
            currency = request.env.user.partner_id.currency_id
            vals = {'partner': partner_id, 'name': user.name, 'image': user.image_1920,
                    'currency': currency,
                    'newpassword': kw.get('data')}
            return {
                'data': request.env['ir.ui.view'].render_template(
                    'aspl_website_customer_wallet.change_pin_template', vals)}
        return {'data': ''}



    @http.route(['/change/pin/process'], type="json", auth="public", website=True)
    def change_pin_process(self, **kw):
        oldpin = kw.get('oldpin')
        newpin = kw.get('newpin')
        set_pin = kw.get('setpin')
        partner_id = request.env.user.partner_id
        currency = request.env.user.partner_id.currency_id
        user = request.env.user
        old_pwd = user.partner_id.customer_password

        if oldpin != old_pwd:
            vals = {'partner': partner_id, 'name': user.name, 'image': user.image_1920,
                    'currency': currency, 'error': '1'}
            return {'data':request.env['ir.ui.view'].render_template(
                'aspl_website_customer_wallet.change_pin_template', vals)}
        else:
            user.partner_id.update({'customer_password': newpin})

        # template_id = request.env.ref(
        #     'aspl_website_customer_wallet.change_pin_email_customer_template')
        template = request.env['res.config.settings'].sudo().search([], order='id desc', limit=1)
        if template and template.change_wallet_pin_template_id:
            template.change_wallet_pin_template_id.send_mail(user.id, force_send=True)

        return {'data': request.env['ir.ui.view'].render_template(
            'aspl_website_customer_wallet.customer_wallet_logging')}

    @http.route(['/add/money'], type="json", auth="public", website=True)
    def add_money(self, **kw):
        if kw.get('data') == 'wallet':
            user = request.env.user
            partner_id = request.env.user.partner_id
            currency = request.env.user.partner_id.currency_id
            vals = {'partner': partner_id, 'name': user.name, 'image': user.image_1920,
                    'currency': currency, 'addwallet':kw.get('data')}
            return {'data':request.env['ir.ui.view'].render_template(
                'aspl_website_customer_wallet.add_money_template', vals)}
        return {'data': ''}

    @http.route(['/wallet/passbook'], type="json", auth="public", website=True)
    def wallet_passbook(self, **kw):
        if kw.get('data') == 'mypassbook':
            user = request.env.user
            partner_id = request.env.user.partner_id
            currency = request.env.user.partner_id.currency_id
            vals = {'partner': partner_id, 'name': user.name,
                    'image': user.image_1920, 'currency': currency,
                    'passbook': kw.get('data')}
            trans = self.transaction_data(kw.get('transaction'))
            vals['trans'] = trans
            print("\n\n\n\n---->>>trans", trans)
            return {
                'data': request.env['ir.ui.view'].render_template(
                    'aspl_website_customer_wallet.passbook_template', vals), 'trans': trans}
        return {'data': ''}

    @http.route(['/add/payment'], type="http", auth="public", website=True)
    def add_payment(self, amount=False, currency_id=None, acquirer_id=None, **kw):
        amount = kw.get('addwallet')
        con_amount = float(amount)
        values = {}
        user = request.env.user.sudo()
        currency_id = currency_id and int(currency_id)\
                      or request.env.user.partner_id.currency_id.id
        currency = request.env['res.currency'].browse(currency_id)
        acquirers = None
        if acquirer_id:
            acquirers = request.env['payment.acquirer'].browse(int(acquirer_id))
        if not acquirers:
            acquirers = request.env['payment.acquirer'].search(
                [('company_id', '=', user.company_id.id),
                 ('state', 'in', ['enabled', 'test'])])

        partner_id = user.partner_id.id if not user._is_public() else False
        wallet_tx = request.env['customer.wallet'].sudo().create({
            'transaction_type': 'credit',
            'partner_id': partner_id,
            'amount': con_amount,
            'currency_id': int(currency_id),
            'date': date.today(),
        })
        values.update({
            'reference': wallet_tx.name,
            'currency': currency,
            'amount': con_amount,
            'return_url': '/wallet_payment/confirm',
            'partner_id': partner_id,
            'bootstrap_formatting': True,
            'error_msg': kw.get('error_msg'),
            'wallet_transaction': True,
        })

        values['acquirers'] = [acq for acq in acquirers if acq.payment_flow == 's2s']
        values['acquirers'] = [acq for acq in acquirers if acq.payment_flow == 'form'
                               and not acq.wallet_acquirer]
        values['pms'] = request.env['payment.token'].search(
            [('acquirer_id', 'in', [acq.id for acq in values['acquirers']])])
        return request.render('aspl_website_customer_wallet.payment_template', values)

    @http.route(['/wallet_payment/transaction/<string:amount>/<string:currency_id>/<path:reference>'],
                type='json',
                auth='public')
    def transaction(self, acquirer_id, reference, amount, currency_id, **kwargs):
        partner_id = request.env.user.partner_id.id if not request.env.user._is_public() else False
        acquirer = request.env['payment.acquirer'].browse(acquirer_id)
        tx = self._get_existing_transaction(reference, float(amount), partner_id,
                                            int(currency_id), int(acquirer_id),
                                            request.session.get('wallet_payment_tx_id'))
        if not tx:
            values = {
                'acquirer_id': int(acquirer_id),
                'reference': reference,
                'amount': float(amount),
                'currency_id': int(currency_id),
                'partner_id': partner_id,
                'type': 'form_save' if acquirer.save_token != 'none'
                                       and partner_id else 'form',
                'wallet_transaction': True,
            }
            tx = request.env['payment.transaction'].sudo().with_context(lang=None).create(values)
            tx.return_url = '/wallet_payment/confirm?tx_id=%d' % tx.id
            PaymentProcessing.add_payment_transaction(tx)
        render_values = {
            'partner_id': partner_id,
        }
        return acquirer.sudo().render(reference, float(amount), int(currency_id),
                                      values=render_values)

    def _get_existing_transaction(self, reference, amount, partner_id,
                                  currency_id, acquirer_id, tx_id):
        PaymentTransaction = request.env['payment.transaction']
        tx = None
        if tx_id:
            tx = PaymentTransaction.sudo().browse(tx_id)
            if not tx.exists() or tx.reference != reference or tx.acquirer_id.id != acquirer_id:
                tx = None

        if not tx:
            tx = PaymentTransaction.sudo().search([('reference', '=', reference),
                                                   ('acquirer_id', '=', acquirer_id)])

        if tx and (
                tx.state != 'draft' or tx.partner_id.id != partner_id or
                tx.amount != amount or tx.currency_id.id != currency_id):
            tx = None

        return tx


    @http.route(['/wallet_payment/transaction/<string:amount>/<string:currency_id>/<path:reference>'],
                type='json',
                auth='public')
    def transaction(self, acquirer_id, reference, amount, currency_id, **kwargs):
        partner_id = request.env.user.partner_id.id if not request.env.user._is_public() else False
        acquirer = request.env['payment.acquirer'].browse(acquirer_id)
        tx = self._get_existing_transaction(reference, float(amount), partner_id,
                                            int(currency_id), int(acquirer_id),
                                            request.session.get('wallet_payment_tx_id'))
        if not tx:
            values = {
                'acquirer_id': int(acquirer_id),
                'reference': reference,
                'amount': float(amount),
                'currency_id': int(currency_id),
                'partner_id': partner_id,
                'type': 'form_save' if acquirer.save_token != 'none'
                                       and partner_id else 'form',
                'wallet_transaction': True,
            }
            tx = request.env['payment.transaction'].sudo().with_context(lang=None).create(values)
            tx.return_url = '/wallet_payment/confirm?tx_id=%d' % tx.id
            PaymentProcessing.add_payment_transaction(tx)

        render_values = {
            'partner_id': partner_id,
        }
        return acquirer.sudo().render(reference, float(amount),
                                      int(currency_id), values=render_values)

    @http.route(['/wallet_payment/token/<string:amount>/<string:currency_id>/<path:reference>'],
                type='http',
                auth='public', website=True)
    def payment_token(self, pm_id, reference, amount, currency_id,
                      return_url=None, **kwargs):
        token = request.env['payment.token'].browse(pm_id)
        order_id = kwargs.get('order_id')
        if not token:
            return request.redirect(
                '/wallet_payment/pay?error_msg=%s' % _('Cannot setup the payment.'))

        partner_id = request.env.user.partner_id.id if not request.env.user._is_public() else False
        wallet_tx = request.env['customer.wallet'].sudo().create({
            'type': 'credit',
            'partner_id': partner_id,
            'amount': float(amount),
            'currency_id': int(currency_id),
            'date': date.today(),
        })
        values = {
            'acquirer_id': token.acquirer_id.id,
            'reference': wallet_tx.name,
            'amount': float(amount),
            'currency_id': int(currency_id),
            'partner_id': partner_id,
            'payment_token_id': pm_id,
            'type': 'form_save' if token.acquirer_id.save_token != 'none'
                                   and partner_id else 'form',
            'wallet_transaction': True,
        }
        if order_id:
            values['sale_order_ids'] = [(6, 0, [order_id])]
        tx = request.env['payment.transaction'].sudo().with_context(lang=None).create(values)
        PaymentProcessing.add_payment_transaction(tx)
        try:
            res = tx.s2s_do_transaction()
            if tx.state == 'done':
                tx.return_url = return_url or '/wallet_payment/confirm?tx_id=%d' % tx.id
            valid_state = 'authorized' if tx.acquirer_id.capture_manually else 'done'
            if not res or tx.state != valid_state:
                tx.return_url = '/wallet_payment/pay?error_msg=%s' % _('Payment transaction failed.')
            return request.redirect('/payment/process')
        except Exception as e:
            return request.redirect('/payment/process')

    @http.route(['/wallet_payment/confirm'], type='http', auth='public', website=True)
    def confirm(self, **kw):
        tx_id = int(kw.get('tx_id', 0)) or request.session.pop('wallet_payment_tx_id', 0)
        if tx_id:
            tx = request.env['payment.transaction'].browse(tx_id).sudo().exists()
            if tx.state == 'done':
                wallet_transaction_id = request.env['customer.wallet'].\
                    search([('name', '=', tx.reference)])
                if wallet_transaction_id:
                    wallet_transaction_id.write({'state': 'done',
                                                 'account_payment_id': tx.payment_id.id,
                                                 'payment_transaction_id': tx.id})
            else:
                payment_acquirer_transfer = request.env.ref('payment.payment_acquirer_transfer')
                if tx:
                    wallet_transaction_id = request.env['customer.wallet'].\
                        search([('name', '=', tx.reference)])
                    if wallet_transaction_id:
                        wallet_transaction_id.wire_transfer_acquirer = True
            return request.redirect('/wallet_payment/confirmation?tx_id=%d' % tx.id)
        else:
            return request.redirect('/my/home')

    @http.route(['/wallet_payment/confirmation'], type='http', auth='public', website=True)
    def confirmation(self, **kw):
        tx_id = int(kw.get('tx_id', 0))
        if tx_id:
            tx = request.env['payment.transaction'].browse(tx_id)
            if tx.state == 'done':
                status = 'success'
                message = tx.acquirer_id.done_msg
            elif tx.state == 'pending':
                status = 'warning'
                message = tx.acquirer_id.pending_msg
            else:
                status = 'danger'
                message = tx.acquirer_id.error_msg
            PaymentProcessing.remove_payment_transaction(tx)
            currency_id = request.env.user.partner_id.currency_id
            if not tx.acquirer_id.id == request.env.ref('payment.payment_acquirer_transfer').id:
                # template = request.env.ref('aspl_website_customer_wallet.added_email_customer_template')
                template = request.env['res.config.settings'].sudo().search([], order='id desc', limit=1)
                if template and template.add_wallet_template_id and tx:
                    wallet_id = request.env['customer.wallet'].search([('name', '=', tx.reference)])
                    # template.write({'email_from': rec.company_id.email})
                    template.add_wallet_template_id.send_mail(wallet_id.id, True,
                                       email_values={'email_to': wallet_id.partner_id.email})
            is_wire_transfer = False
            if tx and tx.acquirer_id.id == request.env.ref('payment.payment_acquirer_transfer').id:
                is_wire_transfer = True
            return request.render('aspl_website_customer_wallet.payment_confirmation',
                                  {'tx': tx, 'is_wire_transfer': is_wire_transfer,
                                   'status': status, 'message': message,
                                   'currency': currency_id})
        else:
            return request.redirect('/my/home')

    def transaction_data(self, data):
        partner_id = request.env.user.partner_id.id
        search_lst = []
        if data == 'credit':
            search_lst = ['credit']
        elif data == 'debit':
            search_lst = ['debit']
        else:
            search_lst = ['credit', 'debit']
        transaction_data = request.env['customer.wallet'].sudo().\
            search([('transaction_type', 'in', search_lst),
                    ('state', '=', 'done'),
                    ('partner_id', '=', partner_id)])
        vals = []
        for transaction in transaction_data:
            if transaction.transaction_type == 'credit':
                tr = 'Added'
            elif transaction.transaction_type == 'debit':
                tr = 'Used'
            vals.append({'date': str(transaction.date), 'amount': transaction.amount,
                         'currency': transaction.currency_id.symbol,
                         'transaction_type': tr})
        return vals

    @http.route('/wallet/data/selection', type='json', auth='public', website=True)
    def data_selection(self, data):
        partner_id = request.env.user.partner_id.id
        search_lst = []
        data1 = self.transaction_data(data)
        return json.dumps(data1)

    @http.route('/wallet/payment/page', type='http', auth='public', website=True)
    def wallet_payment_page(self, **kwargs):
        wallet_id = qcontext['page_name'] = 'payment'
        vals = {'wallet_id': wallet_id}
        return request.render('aspl_website_customer_wallet.payment_inherit', vals)


class WebsitePartialPayment(http.Controller):

    @http.route(['/sale/partial_pay/price'], type="json", auth="public", website=True)
    def add_partial_amount(self, amount):
        amount = float(amount)
        order = request.website.sale_get_order()
        order.partial_pay_amount = amount

    @http.route(['/invoice/partial_pay/price'], type="json", auth="public", website=True)
    def add_partial_invoice_amount(self, amount, invoice):
        invoice_id = request.env['account.move'].sudo().browse(int(invoice))
        amount = float(amount)
        if invoice_id:
            invoice_id.sudo().partial_pay = amount

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
