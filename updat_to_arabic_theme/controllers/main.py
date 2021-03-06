import json
import logging
import base64
import json
import math
import time
import datetime

from werkzeug import urls

from odoo import fields as odoo_fields, http, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError, MissingError, UserError
from odoo.http import content_disposition, Controller, request, route
from odoo.tools import consteq

class Website_sale_update(http.Controller):
    @route(['/shop/payment/date'], type='http', auth='user', website=True)
    def update_date(self, redirect=None, **post):
        order = request.website.sale_get_order()
        if post and request.httprequest.method == 'POST':
            if post['input_date']=="":
                date = order.expected_date
            else:
                date=post['input_date'][:len(post['input_date'])-3]
            print(date)
            try:
                date = datetime.datetime.strptime(date, '%m/%d/%Y %H:%M')
            except:
                date = order.expected_date
                print(date)
            print(date)
            order.update({
                'commitment_date':date
            })
            return request.redirect('/shop/payment')






