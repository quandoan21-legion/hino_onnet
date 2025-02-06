from odoo import models, fields


class ApproveHistory(models.Model):
    _name = 'approve.history'
    _description = 'Approval History'

    employee_id = fields.Many2one('hr.employee', string="Người xác nhận", required=True)
    department_id = fields.Many2one('hr.department', string="Phòng ban", related="employee_id.department_id", readonly=True)
    position_id = fields.Many2one('hr.job', string="Chức vụ", related="employee_id.job_id", readonly=True)
    status_from = fields.Char(string="Từ trạng thái", required=True)
    status_to = fields.Char(string="Đến trạng thái", required=True)
    approve_date = fields.Date(string="Ngày xác nhận", required=True)
    note = fields.Text(string="Lý do")
    rank_upgrade_id = fields.Many2one('customer.rank.upgrade', string="Nâng hạng khách hàng")
    customer_rank_upgrade_id = fields.Many2one(
    'customer.rank.upgrade', string="Nâng hạng khách hàng", ondelete="cascade"
)
