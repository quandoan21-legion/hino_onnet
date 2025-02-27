from odoo import models, fields, api
from datetime import date

class SalesRequestApproval(models.Model):
    _name = 'sales.request.approval'
    _description = 'Sales Request Approval History'
    _order = 'x_confirm_date desc, id desc'

    x_request_id = fields.Many2one('sale.request', string='Request',  ondelete='cascade')
    x_confirmer_id = fields.Many2one('hr.employee', string='Approval Person')
    x_department_id = fields.Many2one('hr.department', string='Department')
    x_position_id = fields.Many2one('hr.job', string='Position')
    x_state_from = fields.Char('From Status')
    x_state_to = fields.Char('To Status')
    x_confirm_date = fields.Date('Confirmation Date', default=fields.Date.today)
    x_reason = fields.Text('Reason')

    @api.model
    def _get_current_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)

    # @api.multi
    # def write(self, vals):
    #     """Kiểm tra khi trạng thái chuyển sang 'approved' và tạo lịch sử phê duyệt"""
    #     res = super(SaleRequest, self).write(vals)
    #
    #     if 'x_state' in vals and vals['x_state'] == 'approved':
    #         employee = self._get_current_employee()
    #         if employee:
    #             self.env['sales.request.approval'].create({
    #                 'x_request_id': self.id,
    #                 'x_confirmer_id': employee.id,
    #                 'x_department_id': employee.department_id.id,
    #                 'x_position_id': employee.job_id.id,
    #                 'x_state_from': 'pending',
    #                 'x_state_to': 'approved',
    #                 'x_confirm_date': date.today(),
    #                 'x_reason': self.x_reason or 'Auto-approved',
    #             })
    #
    #     return res