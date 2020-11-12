import requests
import base64
import urllib3

from PIL import Image
from odoo import models, fields, api, _


class ProductImage(models.Model):
    _inherit = 'product.template'

    image_url = fields.Char(string='Image URL')


    def import_images(self):
        """ function to load image from URL """
        list=[]
        for i in self.env['product.template'].search([('default_code','!=',False),('product_brand_ept_id','!=',False)]):
            image = False
            ir=i.default_code
            brand=i.product_brand_ept_id.name

            try :
                path='/home/enas/erp/custom_addons/Trend/elfgala/product_image_import/static/img/' + brand + '/' + ir+'.jpg'
                path2='/home/enas/erp/custom_addons/Trend/elfgala/product_image_import/static/img/Sarr Design/54031101001.jpg'
                with open(path, "rb") as img_file:
                    image64 = base64.b64encode(img_file.read())
                # image64 = base64.b64encode(image)
                    i.image_1920 = image64
            except :
                if i.product_brand_ept_id.logo:
                    i.image_1920 = i.product_brand_ept_id.logo
                else:
                    path ='/home/enas/erp/custom_addons/Trend/elfgala/product_image_import/static/img/Al Fagalla.jpeg'
                    with open(path, "rb") as img_file:
                        image64 = base64.b64encode(img_file.read())
                        i.image_1920 = image64
                print(ir)
                list.append(ir)
                pass
        if list:
            mess=''
            for i in list:
                mess +=" "+i
            return {'warning': {
                'title': _('Warning'),
                'message': _('photos of '+mess+' not uploaded')
            }}



# class ProductVariantImage(models.Model):
#     _inherit = 'product.product'
#
#     image_url = fields.Char(string='Image URL')
#
#     @api.onchange('image_url')
#     def _onchange_image_url(self):
#         """ function to load image from URL in product variant"""
#         image = False
#         if self.image_url:
#             image = base64.b64encode(requests.get(self.image_url).content)
#         self.image_1920 = image