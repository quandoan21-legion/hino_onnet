from odoo import models, fields

class CRMContract(models.Model):
    _name = 'crm.contract'
    _description = "Create, track and manage dealer and customer contracts"

    contract_line_ids = fields.One2many(
        'crm.contract.line',
        'contract_id',
        string="Contract Line",
    )
    status = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress','In Progress'),
        ('completed','Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    contract_code = fields.Char(
        string="Contract code",
        required=True,
        readonly=True,
        default="COXXXXXX"
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
    attachment_ids = fields.Many2many(
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
    dealer_branch_id = fields.Many2one(
        'res.company',
        string="Dealer branch",
        tracking=True,
    )
    salesperson_id = fields.Many2one(
        'hr.employee',
        domain=[('job_title', '=', 'Sales staff')],
        string="Salesperson",
    )
    purchase_type = fields.Selection(
        selection = lambda self: self.env['crm.lead']._fields['x_purchase_type'].selection
    )