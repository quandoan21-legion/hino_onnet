from odoo import models, fields, api

class CustomLeadLine(models.Model):
    _name = 'owned.team.car.line'

    lead_id = fields.Many2one('crm.lead', string='Lead')

    model_name = fields.Char(string='Range of vehicle')
    quantity = fields.Integer(string='Number')
    brand_car = fields.Char(string='Car Firm Name')