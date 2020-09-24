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
import psycopg2

from odoo import http, _
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
from odoo.addons.payment.controllers.portal import PaymentProcessing

_logger = logging.getLogger(__name__)

class PaymentProcessing(PaymentProcessing):

    @http.route(['/payment/process/poll'], type="json", auth="public")
    def payment_status_poll(self):
        # retrieve the transactions
        tx_ids_list = self.get_payment_transaction_ids()

        payment_transaction_ids = request.env['payment.transaction'].sudo().search([
            ('id', 'in', list(tx_ids_list)),
            ('date', '>=',
             (datetime.now() - timedelta(days=1)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
        ])
        if not payment_transaction_ids:
            return {
                'success': False,
                'error': 'no_tx_found',
            }

        processed_tx = payment_transaction_ids.filtered('is_processed')
        self.remove_payment_transaction(processed_tx)

        # create the returned dictionnary
        result = {
            'success': True,
            'transactions': [],
        }
        # populate the returned dictionnary with the transactions data
        for tx in payment_transaction_ids:
            message_to_display = tx.acquirer_id[tx.state + '_msg'] if tx.state in\
                                                                      ['done', 'pending', 'cancel',
                                                                       'error'] else None
            tx_info = {
                'reference': tx.reference,
                'state': tx.state,
                'return_url': tx.return_url,
                'is_processed': tx.is_processed,
                'state_message': tx.state_message,
                'message_to_display': message_to_display,
                'amount': tx.amount,
                'currency': tx.currency_id.name,
                'acquirer_provider': tx.acquirer_id.provider,
            }
            tx_info.update(tx._get_processing_info())
            result['transactions'].append(tx_info)

        tx_to_process = payment_transaction_ids.\
            filtered(lambda x: x.state == 'done' and x.is_processed is False)
        try:
            tx_to_process._post_process_after_done()
        except psycopg2.OperationalError as e:
            request.env.cr.rollback()
            result['success'] = False
            result['error'] = "tx_process_retry"
        except Exception as e:
            request.env.cr.rollback()
            result['success'] = False
            result['error'] = str(e)
            _logger.exception(
                "Error while processing transaction(s) %s, exception \"%s\"",
                tx_to_process.ids, str(e))
        if payment_transaction_ids:
            for payment_transaction in payment_transaction_ids:
                if payment_transaction and payment_transaction.invoice_ids\
                        and payment_transaction.invoice_ids.partial_pay:
                    wallet_transaction_id1 = request.env['customer.wallet'].search(
                        [('reference', '=',
                          str(payment_transaction.reference) + '' + 'Wallet'),
                         ('partner_id', '=', payment_transaction.partner_id.id),
                         ('transaction_type', '=', 'debit')])
                    if wallet_transaction_id1:
                        wallet_transaction_id1.update({
                            'state': payment_transaction.state
                        })
                        # template = request.env.ref(
                        #     'aspl_website_customer_wallet.used_in_invoice_email_customer_template')
                        template = request.env['res.config.settings'].sudo().search([], order='id desc', limit=1)
                        if template and template.used_wallet_template_id and wallet_transaction_id1:
                            template.used_wallet_template_id.send_mail(wallet_transaction_id1.id, True,
                                               email_values={'email_to': wallet_transaction_id1.partner_id.email})
                    if payment_transaction and payment_transaction.state == 'done'\
                            and wallet_transaction_id1:
                        tx1 = request.env['payment.transaction'].sudo().search(
                            [('reference', '=', str(payment_transaction.reference) + '-' + 'Wallet'),
                             ('partner_id', '=', payment_transaction.partner_id.id),
                             ('invoice_ids', '=', wallet_transaction_id1.invoice_id.id),
                             ('acquirer_id', '=',
                              request.env['payment.acquirer'].search([('wallet_acquirer', '=', True)], limit=1).id)]),
                        if tx1:
                            tx1[0].state = payment_transaction.state
                elif payment_transaction and payment_transaction.invoice_ids and\
                        not payment_transaction.invoice_ids.partial_pay and\
                        payment_transaction.acquirer_id.wallet_acquirer:
                    wallet_transaction_id1 = request.env['customer.wallet'].search(
                        [('invoice_id', '=', payment_transaction.invoice_ids.id),
                         ('partner_id', '=', payment_transaction.partner_id.id),
                         ('transaction_type', '=', 'debit')])
                    # template = request.env.ref(
                    #     'aspl_website_customer_wallet.used_in_invoice_email_customer_template')
                    template = request.env['res.config.settings'].sudo().search([], order='id desc', limit=1)
                    if template and template.used_wallet_template_id and wallet_transaction_id1:
                        template.used_wallet_template_id.send_mail(wallet_transaction_id1.id, True,
                                           email_values={'email_to': wallet_transaction_id1.partner_id.email})
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
