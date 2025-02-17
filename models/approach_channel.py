from odoo import fields, models, api


class AccessModel(models.Model):
    _name = 'approach.channel'
    _rec_name = 'x_approach_channel'

    x_code = fields.Char(string='Code')
    x_approach_channel = fields.Char(string='Approce Channel')

    @api.model
    def create(self, vals):
        latest_code = self.env['approach.channel'].search([], order='x_code desc', limit=1)
        next_number = 1
        if latest_code and latest_code.x_code:
            next_number = int(latest_code.x_code.replace("channel_", "")) + 1

        vals["x_code"] = f"channel_{next_number:03d}"
        return super().create(vals)
