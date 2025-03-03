from odoo import models, fields, api

class VehicleInterest(models.Model):
    _inherit = 'crm.lead.vehicle.interest.line'

    bid_authorization_id = fields.Many2one('bid.authorization', string='Bid Authorization')