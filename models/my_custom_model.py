from odoo import models, fields

class MyCustomModel(models.Model):
    _name = 'my.model'
    _description = 'My Custom Model'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')