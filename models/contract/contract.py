from odoo import models, fields, api
from datetime import datetime

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
        default="COXXXXXX",
    )
    lead_code_id = fields.Many2one(
        'crm.lead',
        string="Lead code",
    )
    customer_id = fields.Many2one(
        'res.partner',
        domain=[('x_customer_type','=',['last_customer','third_party','body_maker'])],
        string="Customer",
    )
    address = fields.Text(
        string="Address",
    )
    customer_class_id = fields.Many2one(
        'customer.rank',
        string="Customer class",
    )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string="Attach",
    )
    project_id = fields.Many2one(
        'crm.lead',
        string="Project",
    ) # this field need condition, or else manual insert
    sign_day = fields.Date(
        string="Sign day",
        # this field need logic to get sign day from this week or last week
    )
    sign_week = fields.Integer(
        string="Sign week",
        # this field need logic to auto get sign week
    )
    # dealer_id in problem
    dealer_id = fields.Many2one(
        'res.company',
        string="Dealer",
        compute="_compute_dealer_id"
    )
    dealer_branch_id = fields.Many2one(
        'res.company',
        string="Dealer branch",
    )
    salesperson_id = fields.Many2one(
        'hr.employee',
        domain=[('job_title', '=', 'Sales staff')],
        string="Salesperson",
    )
    purchase_type = fields.Selection(
        selection = lambda self: self.env['crm.lead']._fields['x_purchase_type'].selection
    )

    @api.model
    def create(self, vals):
        """
        create contract code sequence base on fiscal year, if not, use this year
        """
        # Get the current fiscal year
        fiscal_year = self.env['account.fiscal.year'].search([], order="date_from desc", limit=1)
        year_suffix = fiscal_year.name[-2:] if fiscal_year else datetime.today().year % 100

        sequence = self.env['ir.sequence'].next_by_code('crm.contract') or "0001"
        vals["contract_code"] = f"C0{year_suffix}{sequence}"

        return super().create(vals)

    @api.constrains('sign_day')
    def _check_sign_day(self):
        """
        logic for sign day here
        """
        return None

    def action_cancel_contract(self):
        """
        logic for cancel button
        """
        self.write({'status': 'cancelled'})

    def sales_info(self):
        """
        placeholder for button sales infomation
        :return:
        """
        return None

    @api.depends('dealer_branch_id')
    def _compute_dealer_id(self):
        for record in self:
            record.dealer_id = record.dealer_branch_id.parent_id if record.dealer_branch_id else False