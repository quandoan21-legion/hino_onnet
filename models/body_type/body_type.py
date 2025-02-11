from odoo import fields, models


class BodyType(models.Model):
    _name = 'hino.body.type'
    _description = 'Body Type Of Vehicle'
    _rec_name = 'rear_body'

    code = fields.Char(string='Body Code', required=True, copy=False, readonly=True, default='To Be Generated')
    rear_body = fields.Char(string='Body Name', required=True)

    _sql_constraints = [
        ('unique_rear_body', 'unique(rear_body)', 'The Body Name must be unique!')
    ]
