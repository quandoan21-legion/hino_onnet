from odoo import models, fields, api

class CRMContractLine(models.Model):
    _name = 'crm.contract.line'
    _description = ""

    contract_id = fields.Many2one(
        'crm.contract',
        string="Contract",
    )
    line_category = fields.Integer(
        string="Category",
    )
    line_end_customer_id = fields.Many2one(
        'res.partner',
        string="End customer",
    )
    line_lead_detail = fields.Many2one(
        'crm.lead.vehicle.interest.line',
        string="Lead detail",
    )
    line_address = fields.Text(
        string="Address",
    )
    line_province_city_id = fields.Many2one(
        'res.country.state',
        string="Province/City",
    )
    line_third_party_offer_ids = fields.Many2many(
        'third.party.registration',
        string="Third Party Offer",
        domain="[('x_customer_id', '=', x_partner_id), ('x_state', '=', 'approved')]"
    )
    model_id = fields.Many2one(
        'product.product',
        string = "Model",
    )
    # Promotion unavailable
    line_barrel_type_id = fields.Many2one(
        'hino.body.type',
        string = "Barrel type",
    )
    line_deposit_status = fields.Selection([
        ('deposited','Deposited'),
        ('not yet deposited','Not Yet Deposited'),
    ], string="Deposit status", tracking=True,)
    line_supply_status = fields.Selection([
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
    line_barrel_state = fields.Selection([
        ('closed','Closed'),
        ('opened', 'Opened'),
    ], string="Barrel state", tracking=True,)
    line_barrel_voucher_state = fields.Selection([
        ('available','Available'),
        ('unavailable','Unavailable'),
    ], string="Barrel voucher state", tracking=True,)
    line_vta_number = fields.Text(
        string="VTA Number",
        help="VTA number accompanying the vehicle with the crane",
    )
    line_payment_method_id = fields.Many2one(
        'payment.method',
        string="Payment methods",
    )
    line_bank_id = fields.Many2one(
        'payment.method',
        string="Bank",
    ) # line_bank_id involve payment_method
    line_payment_status = fields.Selection([
        ('paid','Paid'),
        ('unpaid','Unpaid'),
    ],string="Payment status", tracking=True,)
    line_expected_month_retail_sales = fields.Float(
        string="Expected month of retail sales",
    )
    line_retail_coupon = fields.Many2one(
        'sale.order',
        string="Retail coupon",
    )
    line_retail_day = fields.Date(
        string="Retail day",
    )
    line_note = fields.Text(
        string="Note",
    )
    line_cancellation_reason = fields.Text(
        string="Cancellation reason",
    )
    line_status = fields.Selection([
        ('in_progress','In Progress'),
        ('cancel','Cancel'),
        ('done','Done'),
    ],string="Status", default="in_progress", tracking=True)

    @api.model
    def create(self, vals):
        """Auto-increment for category field"""
        if 'contract_id' in vals:
            existing_count = self.search_count([
                ('contract_id','=',vals['contract_id'])
            ])
            vals['line_category'] = existing_count + 1
        return super().create(vals)
