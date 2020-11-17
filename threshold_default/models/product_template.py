from odoo import fields, models, api


class ThresholdProductTemplate(models.Model):
    _inherit = 'product.template'

    available_threshold = fields.Float(string='Availability Threshold', default=0.0)



class ThresoldResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def get_values(self):
        res = super(ThresoldResConfigSettings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        res.update(inventory_availability=IrDefault.get('product.template', 'inventory_availability') or 'never',
                   available_threshold=IrDefault.get('product.template', 'available_threshold') or 0.0)
        return res
