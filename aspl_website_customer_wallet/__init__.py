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

from . import controllers
from . import models
from odoo import api, SUPERUSER_ID


def init_settings(env):
    for website in env['website'].search([]):
        website.add_wallet_template_id = env.ref('aspl_website_customer_wallet.added_email_customer_template').id
        website.used_wallet_template_id = env.ref('aspl_website_customer_wallet.used_email_customer_template').id
        website.change_wallet_pin_template_id = env.ref('aspl_website_customer_wallet.change_pin_email_customer_template').id


def _set_email(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    init_settings(env)
