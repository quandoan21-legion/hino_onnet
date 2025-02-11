from odoo import api, models

class BodyTypeMethods(models.Model):
    _inherit = 'hino.body.type'

    @api.model
    def create(self, vals):
        if vals.get('code', 'To Be Generated') == 'To Be Generated':
            vals['code'] = self.env['ir.sequence'].next_by_code('hino.body.type') or '/'
        return super(BodyTypeMethods, self).create(vals)
