from odoo import models, fields, api

class CustomLeadLine(models.Model):
    _name = 'member.line'

    lead_id = fields.Many2one('crm.lead', string='Lead')

    x_readonly_fields = fields.Boolean(related='lead_id.x_readonly_fields', store=True)
    # Notebook
    member_id = fields.Many2one('res.partner', string="Member's Name")