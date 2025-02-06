from odoo import models, fields


class CustomLeadLine(models.Model):
    _name = 'owned.team.car.line'

    lead_id = fields.Many2one('crm.lead', string='Lead')

    x_readonly_fields = fields.Boolean(related='lead_id.x_readonly_fields', store=True)
    model_name = fields.Char(string='Range of vehicle')
    quantity = fields.Integer(string='Number')
    brand_car = fields.Char(string='Car Firm Name')