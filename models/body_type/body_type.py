from odoo import fields, models, api

class BodyType(models.Model):
    _name = 'hino.body.type'
    _description = 'Body Type Of Vehicle'
    _rec_name = 'rear_body'

    code = fields.Char(string='Body Code', required=True, copy=False, readonly=True, default='To Be Generated')
    rear_body = fields.Char(string='Body Name', required=True)

    @api.model
    def create(self, vals):
        if vals.get('code', 'To Be Generated') == 'To Be Generated':  # Ensure sequence is only assigned if not provided
            vals['code'] = self.env['ir.sequence'].next_by_code('hino.body.type') or '/'
        return super(BodyType, self).create(vals)
