from odoo import models, fields

class BidAuthorizationApprovalLine(models.Model):
    _name = 'bid.authorization.approve.history'
    _description = 'Bid Authorization Approve History'

    bid_authorization_id = fields.Many2one('bid.authorization', string='Bid Authorization', required=True)

    state_from = fields.Char(string='State From')
    state_to = fields.Char(string='State To')
    confirm_date = fields.Date(string='Confirm Date')
    reason = fields.Text(string='Reason')