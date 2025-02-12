from odoo import models, fields, api
from datetime import datetime

class CRMContract(models.Model):
    _name = 'crm.contract'
    _description = "Create, track and manage dealer and customer contracts"

    status = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress','In Progress'),
        ('completed','Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    contract_code = fields.Char(
        string='Contract code',
        readonly=True,
        copy=False,
        tracking=True,
    )
    customer_id = fields.Many2one(
        'res.partner',
        string="Customer",
        tracking=True,
    )
    lead_code_id = fields.Many2one(
        'crm.lead',
        string="Lead code",
        tracking=True,
    )
    address = fields.Text(
        string="Address",
        tracking=True,
    )
    customer_class_id = fields.Many2one(
        'customer.rank',
        string="Customer class",
        tracking=True,
    )
    attachment_ids = fields.Many2one(
        'ir.attachment',
        string="Attach",
        tracking=True,
    )
    # Mã dự án missing
    sign_day = fields.Date(
        string="Sign day",
        tracking=True,
    )
    sign_week = fields.Date(
        string="Sign week",
        tracking=True,
    )
    dealer_id = fields.Many2one(
        'dealer.group',
        string="Dealer",
        readonly=True,
    )
    dealer_branch_id = fields.Many2one(
        'res.company',
        string="Dealer branch",
        tracking=True,
    )
    salesperson_id = fields.Many2one(
        'hr.employee',
        domain=[('job_title', '=', 'Sales staff')],
        string="Salesperson"
    )
    purchase_type = fields.Selection(
        selection = lambda self: self.env['crm.lead']._field['x_purchase_type'].selection
    )

@api.model
def create(self, vals):

    # Get the current fiscal year
    fiscal_year = self.env['account.fiscal.year'].search([], order="date_from desc", limit=1)
    year_suffix = fiscal_year.name[-2:] if fiscal_year else datetime.today().year%100

    sequence = self.env['ir.sequence'].next_by_code('crm.contract') or "0001"
    vals["contract_code"] = f"C0{year_suffix}{sequence}"

    return super().create(vals)
