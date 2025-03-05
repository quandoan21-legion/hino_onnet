from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CustomLead(models.Model):
    _inherit = 'crm.lead'

    def action_view_bid_authorization(self):
        if self.env['bid.authorization'].search_count([('lead_code_id', '=', self.id)]) == 0:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Bid Authorization',
                'view_mode': 'form',
                'res_model': 'bid.authorization',
                'target': 'new',
                'context': {
                    'default_lead_code_id': self.id,
                    'default_dealer_id': self.x_dealer_id.id,
                    'default_investor_name': self.x_partner_name,
                    'default_investor_address': self.x_contact_address_complete,
                    'default_project_name': self.x_project,
                    'default_area': self.x_area,
                    'default_bid_package_name': self.x_bidding_package,
                    'default_bid_opening_time': self.x_estimated_time_of_bid_opening,
                    'default_vehicle_interest_ids': [(6, 0, self.x_vehicle_interest_ids.ids)],
                }
            }
        else:
            raise ValidationError('Bid Authorization already exists for this lead')   

    def unlink(self):
        for record in self:
            related_bid_authorization = self.env['bid.authorization'].search([('lead_code_id', '=', record.id)])
            if related_bid_authorization and related_bid_authorization.state == 'draft':
                related_bid_authorization.unlink()
            if record.x_vehicle_interest_ids:
                record.x_vehicle_interest_ids.unlink()
        return super().unlink()

    @api.onchange('x_dealer_id', 'x_partner_name', 'x_contact_address_complete', 'x_project', 'x_area', 'x_bidding_package', 'x_estimated_time_of_bid_opening', 'x_vehicle_interest_ids')
    def _onchange_x_dealer_id(self):
        related_bid_authorization = self.env['bid.authorization'].search([('lead_code_id', '=', self._origin.id)])
        if related_bid_authorization and related_bid_authorization.state == 'draft' and self.x_status == 'draft':
            related_bid_authorization.write({'dealer_id': self.x_dealer_id.id,
                                             'investor_name': self.x_partner_name,
                                             'investor_address': self.x_contact_address_complete,
                                             'project_name': self.x_project,
                                             'area': self.x_area,
                                             'bid_package_name': self.x_bidding_package,
                                             'bid_opening_time': self.x_estimated_time_of_bid_opening,
                                             'vehicle_interest_ids': [(6, 0, self.x_vehicle_interest_ids.ids)]})