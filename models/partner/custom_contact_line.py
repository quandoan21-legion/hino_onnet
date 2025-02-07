from odoo import models, fields, api

class CustomContactLine(models.Model):
    _name = 'contact.line'

    x_partner_id = fields.Many2one('res.partner', string='Partner')
    x_district = fields.Char(string='Department')
    x_state_id = fields.Many2one('res.country.state', string='State/Province')
    x_function = fields.Char(string='Function')
