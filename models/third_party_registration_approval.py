from odoo import models, fields

class ThirdPartyRegistrationApproval(models.Model):
    _name = 'third.party.registration.approval'
    _description = 'Third Party Registration Approval'

    registration_id = fields.Many2one('third.party.registration', string='Registration', required=True, ondelete='cascade')
    x_approval_person = fields.Many2one('res.users', string='Person Approval', required=True)
    x_department = fields.Many2one('hr.department', string='Department')
    x_position = fields.Many2one('hr.job', string='Position')
    x_previous_state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], string='Previous Status')
    x_new_state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], string='New Status', required=True)
    x_approval_date = fields.Datetime(string='Approval Date', default=fields.Datetime.now)