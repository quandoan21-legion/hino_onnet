from odoo import models, fields


class SalesRequestApproval(models.Model):
    _name = 'sales.request.approval'
    _description = 'Sales Request Approval History'
    _order = 'x_confirm_date desc, id desc'

    x_request_id = fields.Many2one('sales.request', string='Request', required=True, ondelete='cascade')
    x_confirmer_id = fields.Many2one('hr.employee', string='Approval Person')
    x_department_id = fields.Many2one('hr.department', string='Department')
    x_position_id = fields.Many2one('hr.job', string='Position')
    x_state_from = fields.Char('From Status')
    x_state_to = fields.Char('To Status')
    x_confirm_date = fields.Date('Confirmation Date', default=fields.Date.today)
    x_reason = fields.Text('Reason')
