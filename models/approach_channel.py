from odoo import fields, models


class AccessModel(models.Model):
    _name = 'approach.channel'

    x_code = fields.Char(string='Code')
    x_approach_channel = fields.Char(string='Approce Channel')


