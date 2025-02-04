from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    vat_number = fields.Char(string='VAT Number', help='Value Added Tax Number')
    identity_number = fields.Char(string='Identity Number', help='National or Personal Identity Number')
