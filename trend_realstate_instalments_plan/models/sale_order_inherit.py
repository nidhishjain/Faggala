# -*-	coding:	utf-8	-*-
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import math


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    @api.onchange('date_order')
    def _get_first_instalments_date(self):
        if self.date_order:
            d2 = fields.Date.from_string(self.date_order).strftime("%Y-%m-%d")
            d2 = fields.Datetime.from_string(d2).date()
            self.first_installment_date = d2 = d2 + relativedelta(months=3)

    installment_ids = fields.One2many(comodel_name="sale.installment", inverse_name="sale_id")
    maintenance_ids = fields.One2many(comodel_name="sale.maintenance", inverse_name="sale_id_main")
    deposit_amount = fields.Float()
    contract_signing_amount = fields.Float()
    delivery_amount = fields.Float()
    delivery_amount_per = fields.Float("Delivery Percentage")
    contract_amount_per = fields.Float("Contract Signing Percentage")
    maintenance_per = fields.Float("Maintenance Percentage")
    maintenance_amount = fields.Float("Maintenance Amount", compute='get_maintenance_amount',
                                      store=True)
    full_unit_price = fields.Float(string='Full Unit Price', compute='get_full_unit_price',
                                   store=True)
    first_installment_date = fields.Date(copy=False, default=_get_first_instalments_date)
    no_of_installments = fields.Integer()
    maintenance_no = fields.Integer()
    payment_type = fields.Selection(string="Payment Type", selection=[('monthly', 'Monthly'),
                                                                      ('quarter', 'Quarter'),
                                                                      ('4_months', '4 Months'),
                                                                      ('semi_annual', 'Semi Annual'),
                                                                      ('annual', 'Annual'),
                                                                      ],
                                    copy=False, default='monthly')

    installment_amount = fields.Float(compute='get_installment_amount',
                                      store=True)

    deposit_amount_date = fields.Date(string='Deposit Date')
    contract_signing_amount_date = fields.Date(string='Contract Signing Date')
    delivery_amount_date = fields.Date(string='Delivery Date')

    @api.constrains('full_unit_price', 'installment_ids')
    def check_total_installment_amount(self):
        for order in self:
            if order.full_unit_price and order.installment_ids:
                if order.full_unit_price != sum(
                        installment.installment_amount for installment in order.installment_ids):
                    raise ValidationError(_('Total installments amount must be equal full unit price.'))

    @api.onchange('contract_amount_per', 'full_unit_price')
    @api.depends('contract_amount_per', 'full_unit_price')
    def get_contract_amount(self):
        for order in self:
            order.contract_signing_amount = order.full_unit_price * (order.contract_amount_per / 100)

    @api.onchange('contract_signing_amount', 'full_unit_price')
    @api.depends('contract_signing_amount', 'full_unit_price')
    def get_contract_per(self):
        for order in self:
            if order.full_unit_price > 0:
                order.contract_amount_per = (order.contract_signing_amount / order.full_unit_price) * 100

    @api.onchange('delivery_amount_per', 'full_unit_price')
    @api.depends('delivery_amount_per', 'full_unit_price')
    def get_delivery_amount(self):
        for order in self:
            order.delivery_amount = order.full_unit_price * (order.delivery_amount_per / 100)

    @api.onchange('delivery_amount', 'full_unit_price')
    @api.depends('delivery_amount', 'full_unit_price')
    def get_delivery_per(self):
        for order in self:
            if order.full_unit_price > 0:
                order.delivery_amount_per = (order.delivery_amount / order.full_unit_price) * 100

    @api.depends('order_line', 'order_line.product_id', 'order_line.product_id.full_unit_price')
    def get_full_unit_price(self):
        for order in self:
            if order.order_line:
                order.full_unit_price = order.order_line[0].product_id.full_unit_price
            else:
                order.full_unit_price = 0.0

    @api.depends('maintenance_per', 'full_unit_price')
    def get_maintenance_amount(self):
        for order in self:
            order.maintenance_amount = order.full_unit_price * (order.maintenance_per / 100)

    @api.depends('deposit_amount', 'contract_signing_amount', 'delivery_amount', 'full_unit_price')
    def get_installment_amount(self):
        for order in self:
            order.installment_amount = order.full_unit_price - (
                    order.deposit_amount + order.contract_signing_amount + order.delivery_amount)

    def _check_data_before_submit(self):
        if not self.first_installment_date:
            raise ValidationError(_("You must provide installment first date before create installments"))

        if not self.deposit_amount_date and self.deposit_amount:
            raise ValidationError(_("You must provide deposit date before create installments"))

        if not self.contract_signing_amount_date and self.contract_signing_amount:
            raise ValidationError(_("You must provide contract signing date before create installments"))

        if not self.delivery_amount_date and self.delivery_amount:
            raise ValidationError(_("You must provide delivery date before create installments"))

        if not self.no_of_installments:
            raise ValidationError(_("You must provide number of installments before create installments"))

        if not self.order_line:
            raise ValidationError(_("You must provide Unit before create installments"))

    def action_create_main(self):
        if self.maintenance_ids:
            self.sudo().maintenance_ids.unlink()
        if not self.maintenance_no:
            raise ValidationError(_("You must provide maintenance number before create maintenance"))

        all_amount = self.full_unit_price * (self.maintenance_per / 100)
        m_amount = all_amount / self.maintenance_no
        for counter in range(0, self.maintenance_no):
            main_vals = {
                "name": counter + 1,
                "sale_id_main": self.id,
                "maintenance_amount": m_amount,

            }
            main_id = self.env['sale.maintenance'].sudo().create(main_vals)
            all_amount = all_amount - m_amount
            if all_amount < m_amount:
                m_amount = all_amount

    def action_create_installments(self):
        self._check_data_before_submit()
        if self.installment_ids:
            self.sudo().installment_ids.unlink()

        installment_date = fields.Date.from_string(self.first_installment_date)
        installment_amount = self.installment_amount / self.no_of_installments
        if self.payment_type == 'monthly':
            months = 1
        elif self.payment_type == 'quarter':
            months = 3
        elif self.payment_type == '4_months':
            months = 4
        elif self.payment_type == 'semi_annual':
            months = 6
        else:
            months = 12
        counter = 0
        installment_vals = []
        for counter in range(1, self.no_of_installments + 1):
            digit_remaining_amount, int_remaining_amount = math.modf(installment_amount)
            remaining_amount = digit_remaining_amount * (self.no_of_installments - 1)
            if counter != (self.no_of_installments):
                installment_vals += [{
                    "sale_id": self.id,
                    "installment_date": installment_date,
                    "installment_amount": int_remaining_amount,
                    "installment_type": 'regular',

                }]
                remaining_amount += digit_remaining_amount
                installment_date = installment_date + relativedelta(months=months)
            elif counter == (self.no_of_installments):
                installment_vals += [{
                    "sale_id": self.id,
                    "installment_date": installment_date,
                    "installment_amount": installment_amount + remaining_amount,
                    "installment_type": 'regular',

                }]
                installment_date = installment_date + relativedelta(months=months)
        if self.contract_signing_amount:
            installment_vals += [{
                "sale_id": self.id,
                "installment_date": fields.Date.from_string(self.contract_signing_amount_date),
                "installment_amount": self.contract_signing_amount,
                "installment_type": 'contract_signing',

            }]

        if self.delivery_amount:
            installment_vals += [{
                "sale_id": self.id,
                "installment_date": fields.Date.from_string(self.delivery_amount_date),
                "installment_amount": self.delivery_amount,
                "installment_type": 'delivery',

            }]
        if self.deposit_amount:
            installment_vals += [{
                "sale_id": self.id,
                "installment_date": fields.Date.from_string(self.deposit_amount_date),
                "installment_amount": self.deposit_amount,
                "installment_type": 'deposit',

            }]
        new_installment_vals = sorted(installment_vals, key=lambda k: k['installment_date'])
        for counter in range(0, len(new_installment_vals)):
            new_installment_vals[counter].update({"name": counter + 1})

        for item in new_installment_vals:
            created_installments = self.env['sale.installment'].sudo().create(item)
