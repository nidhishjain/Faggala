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
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    customer_wallet = fields.Boolean()
    add_wallet_template_id = fields.Many2one(related='website_id.add_wallet_template_id',
                                             string="Add Wallet Mail Template", readonly=False)
    used_wallet_template_id = fields.Many2one(related='website_id.used_wallet_template_id',
                                              string="Used Wallet In Sale Mail Template", readonly=False)
    change_wallet_pin_template_id = fields.Many2one(related='website_id.change_wallet_pin_template_id',
                                                    string="Change Wallet Pin Mail Template", readonly=False)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param_obj = self.env['ir.config_parameter'].sudo()
        res.update({'customer_wallet':
                        param_obj.sudo().get_param('aspl_website_customer_wallet.customer_wallet'),
                    })
        return res

    def set_values(self):
        param_obj = self.env['ir.config_parameter'].sudo()
        param_obj.sudo().set_param('aspl_website_customer_wallet.customer_wallet',
                                   self.customer_wallet)
        return super(ResConfigSettings, self).set_values()


class Website(models.Model):
    _inherit = 'website'

    def _default_add_wallet_mail_template(self):
        try:
            return self.env.ref('aspl_website_customer_wallet.added_email_customer_template').id
        except ValueError:
            return False

    def _default_used_wallet_mail_template(self):
        try:
            return self.env.ref('aspl_website_customer_wallet.used_email_customer_template').id
        except ValueError:
            return False

    def _default_change_wallet_pin_template(self):
        try:
            return self.env.ref('aspl_website_customer_wallet.change_pin_email_customer_template').id
        except ValueError:
            return False

    add_wallet_template_id = fields.Many2one('mail.template',
                                             default=_default_add_wallet_mail_template,
                                             string="Add Wallet Mail Template")
    used_wallet_template_id = fields.Many2one('mail.template',
                                              default=_default_used_wallet_mail_template,
                                              string="Used Wallet In Sale Mail Template")
    change_wallet_pin_template_id = fields.Many2one('mail.template',
                                                    default=_default_change_wallet_pin_template,
                                                    string="Change Wallet Pin Mail Template")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
