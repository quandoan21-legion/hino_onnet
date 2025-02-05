from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_company_type = fields.Selection(
        [
            ('personal', 'Personal'),
            ('company', 'Company'),
            ('internal_hmv', 'Internal_HMV')
        ],
        string="Customer Status",
        default='personal'
    )
    x_dealer_id = fields.Char(string='Dealer', readonly=True) # liên quan đến dealer.group - chưa có giải thích cụ thể
    x_dealer_branch_id = fields.Many2one('res.company', string='Dealer Branch', default=lambda self: self.env.company, tracking=True, readonly=True)
    x_customer_type = fields.Selection(
        [('draft', 'Draft'), ('third_party', 'Third Party'), ('body_maker', 'Body Maker')],
        string='Customer Type', default='draft', tracking=True
    )
    x_name = fields.Char(string='Customer Name', store=True, tracking=True)
    x_customer_code = fields.Char(string='Customer Code', tracking=True)
    x_contact_address = fields.Char(string="Contact Address",help="Customer's detailed address.")
    x_district = fields.Char(string='District')
    x_state_id = fields.Many2one('res.country.state', string="State/Province")
    x_field_sale_id = fields.Char(string='Field Sale') # liên quan đến khu vực bán hàng 2.2.2 dùng many2one relation {Khu vực bán hàng}
    x_currently_rank_id = fields.Many2one('customer.rank', string='Currently Rank')
    x_business_registration_id = fields.Char(string='Business Registration ID', help='Business Registration ID')
    x_identity_number = fields.Char(string='Identity Number', help='National or Personal Identity Number')
    x_website = fields.Char(string="Website")
    x_phone = fields.Char(string='Phone number', tracking=True)
    x_mobile = fields.Char(string='Mobile number', tracking=True)
    x_industry_id = fields.Many2one('res.partner.industry', string='Business Field', tracking=True)
    x_activity_area = fields.Char(string='Activity Area', tracking=True)
    x_service_contract = fields.Boolean(string='Service Contact', tracking=True)
    x_number_of_vehicles = fields.Integer(string='Number of Vehicles')
    x_hino_vehicle = fields.Integer(string='Hino Vehicle')
    x_number_repair_order = fields.Integer(string='Number of Repair Order')
    x_repair_order_from_id = fields.Integer(string='Repair Order From') # liên quan đến nhóm 2 dùng repair.order field
    x_repair_order_to_id = fields.Integer(string='Repair Order To') # liên quan đến nhóm 2 dùng repair.order field
    x_cumulative_points = fields.Integer(string='Cumulative Points')
    x_register_sale_3rd_id = fields.Char(string='Register Sale 3rd') # liên quan đến phần 2.2.3 dùng many2one relation
