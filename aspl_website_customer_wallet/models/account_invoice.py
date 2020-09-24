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
from odoo.exceptions import UserError, ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.move"

    partial_pay = fields.Float(string="Partial Payment Amount")

    def _create_payment_transaction(self, vals):
        '''Similar to self.env['payment.transaction'].create(vals) but the
        values are filled with the
        current invoices fields (e.g. the partner or the currency).
        :param vals: The values to create a new payment.transaction.
        :return: The newly created payment.transaction record.
        '''
        # Ensure the currencies are the same.
        currency = self[0].currency_id
        if any([inv.currency_id != currency for inv in self]):
            raise ValidationError(_(
                'A transaction can\'t be linked to invoices having different currencies.'))

        # Ensure the partner are the same.
        partner = self[0].partner_id
        if any([inv.partner_id != partner for inv in self]):
            raise ValidationError(_(
                'A transaction can\'t be linked to invoices having different partners.'))

        # Try to retrieve the acquirer. However, fallback to the token's acquirer.
        acquirer_id = vals.get('acquirer_id')
        acquirer = None
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
            raise ValidationError(_('A journal must be specified of the acquirer %s.'
                                    % acquirer.name))

        if not acquirer_id and acquirer:
            vals['acquirer_id'] = acquirer.id
        amount = sum(self.mapped('amount_residual')) - self.partial_pay
        vals.update({
            'amount': amount or sum(self.mapped('amount_residual')),
            'currency_id': currency.id,
            'partner_id': partner.id,
            'invoice_ids': [(6, 0, self.ids)],
        })
        transaction = self.env['payment.transaction'].create(vals)
        if self.partial_pay:
            vals.update({
                'reference': str(transaction.reference) + '-' + 'Wallet',
                'acquirer_id': self.env['payment.acquirer'].search([('wallet_acquirer', '=', True)],
                                                                   limit=1).id,
                'amount': self.partial_pay,
                'currency_id': currency.id,
                'partner_id': partner.id,
                'invoice_ids': [(6, 0, self.ids)],
            })
            self.env['payment.transaction'].create(vals)
        # Process directly if payment_token
        if transaction.payment_token_id:
            transaction.s2s_do_transaction()
        return transaction

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
