from odoo import models, fields, api

class CRMContractLine(models.Model):
    _name = 'crm.contract.line'
    _description = ""

    contract_id = fields.Many2one(
        'crm.contract',
        string="Contract",
    )
    category = fields.Integer(
        string="Category",
    )
    end_customer_id = fields.Many2one(
        'res.partner',
        string="End customer",
    )
    lead_detail = fields.Many2one(
        'crm.lead.vehicle.interest.line',
        string="Lead detail",
    )
    address = fields.Text(
        string="Address",
    )
    province_city_id = fields.Many2one(
        'res.country.state',
        string="Province/City",
    )
    third_party_offer_ids = fields.Many2many(
        'third.party.registration',
        'contract_id',
        'x_registration_code',
        string="",
        compute="_compute_approved_offers",
    )
    # model_id = fields.Many2one(
    #     'product.product',
    #     string = "Model",
    #     domain = [('category', '=', ['CKD','CBU'])], # don't know what is this
    #     tracking = True,
    # )
    # Promotion missing
    barrel_type_id = fields.Many2one(
        'hino.body.type',
        string = "Barrel type",
    )
    deposit_status = fields.Selection([
        ('deposited','Deposited'),
        ('not yet deposited','Not Yet Deposited'),
    ], string="Deposit status", tracking=True,)
    supply_status = fields.Selection([
        ('Available in stock','Available in stock'),
        ('Allocation from HMV','Allocation from HMV'),
    ], string="Supply status", tracking=True,)
    # vin_expected_to_be_allocated_id = fields.Many2one(
    #     'stock.lot', # placeholder, data still unavailable
    #     string="Vin expected to be allocated/PO",
    # )
    # engine_number_id = fields.Many2one(
    #     'master.data.vin', # placeholder, data still unavailable
    #     string = "Engine Number",
    #     help = "Engine number corresponds to vin number"
    # )
    barrel_state = fields.Selection([
        ('closed','Closed'),
        ('opened', 'Opened'),
    ], string="Barrel state", tracking=True,)
    barrel_voucher_state = fields.Selection([
        ('available','Available'),
        ('unavailable','Unavailable'),
    ], string="Barrel voucher state", tracking=True,)
    vta_number = fields.Text(
        string="VTA Number",
        help="VTA number accompanying the vehicle with the crane",
    )
    payment_method_id = fields.Many2one(
        'payment.method',
        string="Payment methods",
    )
    bank_id = fields.Many2one(
        'payment.method',
        string="Bank",
    )
    payment_status = fields.Selection([
        ('paid','Paid'),
        ('unpaid','Unpaid'),
    ],string="Payment status", tracking=True,)
    expected_month_retail_sales = fields.Float(
        string="Expected month of retail sales",
    )
    retail_coupon = fields.Many2one(
        'sale.order',
        string="Retail coupon",
    )
    retail_day = fields.Date(
        string="Retail day",
    )
    note = fields.Text(
        string="Note",
    )
    cancellation_reason = fields.Text(
        string="Cancellation reason",
    )
    status = fields.Selection([
        ('in_progress','In Progress'),
        ('cancel','Cancel'),
        ('done','Done'),
    ],string="Status", default="in_progress", tracking=True)

    @api.depends('end_customer_id', 'x_new_state')
    def _compute_approve_offers(self):
        """
        collect the newest status from third party that is "approved" and associated with end customer
        """
        for contract in self:
            if contract.end_customer_id:
                contract.third_party_offer_ids = self.env['third.party.registration'].search([
                    ()
                ])
