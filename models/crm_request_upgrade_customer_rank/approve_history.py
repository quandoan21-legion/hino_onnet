from odoo import models, fields


class ApproveHistory(models.Model):
    _name = 'approve.history'
    _description = 'Approval History'

    employee_id = fields.Many2one('hr.employee', string="Approver", required=True,readonly=True)
    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id", readonly=True)
    position_id = fields.Many2one('hr.job', string="Position", related="employee_id.job_id", readonly=True)
    status_from = fields.Char(string="From Status", required=True, readonly=True)
    status_to = fields.Char(string="To Status", required=True,readonly=True)
    approve_date = fields.Date(string="Approval Date", required=True,readonly=True)
    note = fields.Text(string="Reason" ,required=True)
    # rank_upgrade_id = fields.Many2one('customer.rank.upgrade', string="Customer Rank Upgrade")
    customer_rank_upgrade_id = fields.Many2one(
        'customer.rank.upgrade', string="Customer Rank Upgrade", ondelete="cascade",readonly=True
    )
