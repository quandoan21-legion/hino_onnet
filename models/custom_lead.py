from odoo import models, fields

class CustomLead(models.Model):
    _inherit = 'crm.lead'

    custom_field = fields.Char(string='Custom Field')