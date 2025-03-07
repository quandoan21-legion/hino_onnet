from odoo import models, fields, api

class VehicleInterest(models.Model):
    _inherit = 'crm.lead.vehicle.interest.line'

    bid_authorization_id = fields.Many2one('bid.authorization', string='Bid Authorization')

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)
        for record in res:
            if record.lead_id:
                related_bid_authorization = record.env['bid.authorization'].search([('lead_code_id', '=', record.lead_id._origin.id)])
                if related_bid_authorization and related_bid_authorization.state == 'draft':
                    related_bid_authorization.write({'vehicle_interest_ids': [(4, record.id)]})
        return res