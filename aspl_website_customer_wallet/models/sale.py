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
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    partial_pay_amount = fields.Float(string="Partial Payment Amount")

    def _create_payment_transaction(self, vals):
        '''Similar to self.env['payment.transaction'].create(vals) but
        the values are filled with the
        current sales orders fields (e.g. the partner or the currency).
        :param vals: The values to create a new payment.transaction.
        :return: The newly created payment.transaction record.
        '''
        # Ensure the currencies are the same.
        currency = self[0].pricelist_id.currency_id
        if any([so.pricelist_id.currency_id != currency for so in self]):
            raise ValidationError(_(
                'A transaction can\'t be linked to sales orders having different currencies.'))

        # Ensure the partner are the same.
        partner = self[0].partner_id
        if any([so.partner_id != partner for so in self]):
            raise ValidationError(_(
                'A transaction can\'t be linked to sales orders having different partners.'))

        # Try to retrieve the acquirer. However, fallback to the token's acquirer.
        acquirer_id = vals.get('acquirer_id')
        acquirer = False
        payment_token_id = vals.get('payment_token_id')

        if payment_token_id:
            payment_token = self.env['payment.token'].sudo().browse(payment_token_id)

            # Check payment_token/acquirer matching or take the acquirer from token
            if acquirer_id:
                acquirer = self.env['payment.acquirer'].browse(acquirer_id)
                if payment_token and payment_token.acquirer_id != acquirer:
                    raise ValidationError(_('Invalid token found! Token acquirer %s != %s') % (
                        payment_token.acquirer_id.name, acquirer.name))
                if payment_token and payment_token.partner_id != partner:
                    raise ValidationError(_('Invalid token found! Token partner %s != %s') % (
                        payment_token.partner.name, partner.name))
            else:
                acquirer = payment_token.acquirer_id

        # Check an acquirer is there.
        if not acquirer_id and not acquirer:
            raise ValidationError(_('A payment acquirer is required to create a transaction.'))

        if not acquirer:
            acquirer = self.env['payment.acquirer'].browse(acquirer_id)

        # Check a journal is set on acquirer.
        if not acquirer.journal_id:
            raise ValidationError(_(
                'A journal must be specified of the acquirer %s.' % acquirer.name))

        if not acquirer_id and acquirer:
            vals['acquirer_id'] = acquirer.id
        amount = sum(self.mapped('amount_total')) - self.partial_pay_amount
        vals.update({
            'amount': amount or sum(self.mapped('amount_total')),
            'currency_id': currency.id,
            'partner_id': partner.id,
            'sale_order_ids': [(6, 0, self.ids)],
        })
        transaction = self.env['payment.transaction'].create(vals)
        if self.partial_pay_amount:
            vals.update({
                'reference': str(transaction.reference) + '' + 'Wallet',
                'acquirer_id': self.env['payment.acquirer'].search([('wallet_acquirer', '=', True)],
                                                                   limit=1).id,
                'amount': self.partial_pay_amount,
                'currency_id': currency.id,
                'partner_id': partner.id,
                'sale_order_ids': [(6, 0, self.ids)],
            })
            self.env['payment.transaction'].create(vals)

        # Process directly if payment_token
        if transaction.payment_token_id:
            transaction.s2s_do_transaction()

        return transaction

    def get_portal_last_transaction(self):
        self.ensure_one()
        return self.transaction_ids[-1].get_last_transaction()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
