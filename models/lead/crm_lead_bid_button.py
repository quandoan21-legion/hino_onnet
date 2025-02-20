from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CustomLead(models.Model):
    _inherit = 'crm.lead'

    def action_view_bid_authorization(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bid Authorization',
            'view_mode': 'form',
            'res_model': 'bid.authorization',
            'target': 'new',
            'context': {
                'default_dealer_id': self.x_dealer_id.id,
                'default_investor_name': self.x_partner_name,
                'default_investor_address': self.x_contact_address_complete,
                'default_project_name': self.x_project,
                'default_area': self.x_area,
                'default_bid_package_name': self.x_bidding_package,
                'default_bid_opening_time': self.x_estimated_time_of_bid_opening,
            }
        }
        