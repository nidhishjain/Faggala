from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResCompany(models.Model):
    _inherit = 'res.company'

    branch7 = fields.Char(string='7th branch name')
    place7_lat = fields.Char(string='7th branch Latitude')
    place7_long = fields.Char(string='7th branch Longitude')

    branch_name8 = fields.Char(string='8th branch name')
    place8_lat = fields.Char(string='8th branch Latitude')
    place8_long = fields.Char(string='8th branch Longitude')

    branch_name6 = fields.Char(string='6th branch name')
    place6_lat = fields.Char(string='6th branch Latitude')
    place6_long = fields.Char(string='6th branch Longitude')


    branch_name1= fields.Char(string='First branch name')
    place1_lat= fields.Char(string='First branch Latitude')
    place1_long= fields.Char(string='First branch Longitude')

    branch_name2 = fields.Char(string='second branch name')
    place2_lat= fields.Char(string='second branch Latitude')
    place2_long = fields.Char(string='second branch Longitude')

    branch_name3 = fields.Char(string='third branch name')
    place3_lat= fields.Char(string='Third branch Latitude')
    place3_long = fields.Char(string='Third branch Longitude')

    branch_name4 = fields.Char(string='Fourth branch name')
    place4_lat= fields.Char(string='Fourth branch Latitude')
    place4_long = fields.Char(string='Fourth branch Longitude')

    branch_name5 = fields.Char(string='Fifth branch name')
    place5_lat = fields.Char(string='Fifth branch Latitude')
    place5_long = fields.Char(string='Fifth branch Longitude')

