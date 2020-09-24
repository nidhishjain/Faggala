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
from odoo.exceptions import UserError
from odoo import api, fields, models, _
import datetime

class CustomerWallet(models.Model):
    _name = 'customer.wallet'
    _order = 'id desc'

    name = fields.Char(string="Name")
    date = fields.Date(string="Date")
    partner_id = fields.Many2one('res.partner', string="Partner")
    transaction_type = fields.Selection([('credit', 'Added'),
                                         ('debit', 'Used')])
    amount = fields.Monetary(string="Amount", currency_field='company_currency_id')
    account_payment_id = fields.Many2one('account.payment', string="Account Payment Id")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id.id,
                                 readonly=True)
    currency_id = fields.Many2one(related='company_id.currency_id', string='Account Currency')
    payment_transaction_id = fields.Many2one('payment.transaction', string='Payment Transaction')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('done', 'Done'),
        ('error', 'Error'),
        ('canceled', 'Canceled')
    ], readonly=True, copy=False, default='draft')

    order_id = fields.Many2one('sale.order', 'Sale Order', readonly=True, copy=False)
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True, copy=False)
    reference = fields.Char('Reference')

    company_currency_id = fields.Many2one(related='company_id.currency_id',
                                          string='Company Currency',
                                          readonly=True, store=True,
                                          help='Utility field to express amount currency')
    wire_transfer_acquirer = fields.Boolean('Wire Transfer Acquirer', default=False)

    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('customer.wallet')
        return super(CustomerWallet, self).create(vals)

    def _payment_transaction_vals(self, vals):

        currency = self[0].partner_id.currency_id
        if any([wallet.partner_id.currency_id != currency for wallet in self]):
            raise ValidationError(_(
                'A transaction can\'t be linked to wallet having different currencies.'))

        # Ensure the partner are the same.
        partner = self[0].partner_id
        if any([wallet.partner_id != partner for wallet in self]):
            raise ValidationError(_(
                'A transaction can\'t be linked to wallets having different partners.'))

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
            raise ValidationError(_(
                'A journal must be specified of the acquirer %s.' % acquirer.name))

        if not acquirer_id and acquirer:
            vals['acquirer_id'] = acquirer.id

        vals.update({
            'amount': self.amount,
            'currency_id': self.partner_id.currency_id.id,
            'partner_id': partner.id,
            'reference': self.id,
        })

        transaction = self.env['payment.transaction'].create(vals)
        # Process directly if payment_token
        if transaction.payment_token_id:
            transaction.s2s_do_transaction()

        return transaction

    def wire_transfer_payment(self):
        PaymentTransaction = self.env['payment.transaction']
        for rec in self:
            if rec.state == 'draft' and rec.wire_transfer_acquirer and rec.partner_id:
                payment_acquirer_transfer = self.env.ref('payment.payment_acquirer_transfer')
                payment_transaction_id = PaymentTransaction.\
                    search([('state', '=', 'pending'),
                            ('reference', '=', rec.name),
                            ('partner_id', '=', rec.partner_id.id),
                            ('acquirer_id', '=', payment_acquirer_transfer.id)])
                if payment_transaction_id and payment_transaction_id.state != 'done':
                    default_journal = payment_transaction_id.acquirer_id.journal_id or self.env[
                        'account.journal'].sudo().search([('type', '=', 'bank')], limit=1)
                    payment_transaction_id.date_validate = datetime.date.today()
                    values = {
                        'payment_type': 'inbound',
                        'partner_type': 'customer',
                        'partner_id': payment_transaction_id.partner_id.id,
                        'amount': payment_transaction_id.amount,
                        'currency_id': payment_transaction_id.currency_id.id,
                        'journal_id': default_journal.id,
                        'payment_date': payment_transaction_id.date_validate
                                        or datetime.date.today(),
                        'payment_transaction_id': payment_transaction_id.id,
                        'payment_method_id': self.env.ref(
                            'account.account_payment_method_manual_in').id,
                    }
                    payment_id = self.env['account.payment'].sudo().create(values)
                    payment_transaction_id['state'] = 'done'
                    rec['state'] = 'done'
                    if payment_id:
                        payment_id.post()
                    # template = self.env.ref('aspl_website_customer_wallet.added_email_customer_template')
                    template = self.env['res.config.settings'].search([], order='id desc', limit=1)
                    if template and template.add_wallet_template_id and payment_transaction_id:
                        wallet_id = self.env['customer.wallet'].search([('name', '=', payment_transaction_id.reference)])
                        template.add_wallet_template_id.send_mail(wallet_id.id, True,
                                           email_values={'email_to': wallet_id.partner_id.email})

    def unlink(self):
        for wallet in self:
            if wallet.state == 'done':
                raise UserError(_(
                    'You can not delete Wallet Transactions which are in Done state!'))
        return super(CustomerWallet, self).unlink()

    def transaction(self, acquirer_id, reference, amount, currency_id):
        partner_id = self.env.user.partner_id.id if not self.env.user._is_public() else False
        acquirer = self.env['payment.acquirer'].browse(acquirer_id)
        tx = self._get_existing_transaction(reference, float(amount), partner_id,
                                            int(currency_id), int(acquirer_id),
                                            self.session.get('wallet_payment_tx_id'))
        if not tx:
            values = {
                'acquirer_id': int(acquirer_id),
                'reference': reference,
                'amount': float(amount),
                'currency_id': int(currency_id),
                'partner_id': partner_id,
                'type': 'form_save' if acquirer.save_token != 'none' and partner_id else 'form',
                'wallet_transaction': True,
            }
            tx = self.env['payment.transaction'].sudo().with_context(lang=None).create(values)
            # tx.return_url = '/wallet_payment/confirm?tx_id=%d' % tx.id
            PaymentProcessing.add_payment_transaction(tx)

        render_values = {
            'partner_id': partner_id,
        }
        return acquirer.sudo().render(reference, float(amount),
                                      int(currency_id), values=render_values)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_ids = fields.One2many('customer.wallet', 'partner_id', string="Customer")
    customer_password = fields.Char(string='password')

    wallet_bal = fields.Monetary('Wallet Balance', compute='_compute_calculate_balance')

    def _compute_calculate_balance(self):
        for rec in self:
            domain = [
                ('account_id', '=', rec.property_account_receivable_id.id),
                ('partner_id', '=', rec._find_accounting_partner(rec).id),
                ('reconciled', '=', False),
                '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
                ('credit', '>', 0), ('debit', '=', 0)
            ]
            lines = self.env['account.move.line'].search(domain)
            main_balance = abs(sum(lines.mapped('amount_residual')))
            rec.update({'wallet_bal': main_balance})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
