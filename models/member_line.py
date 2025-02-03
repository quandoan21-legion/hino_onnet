from odoo import models, fields, api

class CustomLeadLine(models.Model):
    _name = 'member.line'

    lead_id = fields.Many2one('crm.lead', string='Lead')

    # Notebook
    member_id = fields.Many2one('res.partner', string="Member's Name")