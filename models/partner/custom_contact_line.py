from odoo import models, fields, api

class CustomContactLine(models.Model):
    _name = 'contact.line'

    x_partner_id = fields.Many2one('res.partner', string='Partner')
    x_type = fields.Selection(
        [
            ('contact', 'Contact'),
            ('invoice address', 'Invoice Address'),
            ('shipping address', 'Shipping Address'),
            ('tracking address', 'Tracking Address'),
            ('other address', 'Other Address'),
        ],
        string="Contact Status",
        default='contact'
    )
    x_name = fields.Char(string='Name')
    x_phone = fields.Char(string='Phone')
    x_mobile = fields.Char(string='Mobile')
    x_email = fields.Char(string='Email')
    x_contact_address = fields.Char(string='Position')
    x_district = fields.Char(string='Department')
    x_state_id = fields.Many2one('res.country.state', string='State/Province')
    x_function = fields.Char(string='Function')
