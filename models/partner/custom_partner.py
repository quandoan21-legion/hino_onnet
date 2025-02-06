from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_potential_count = fields.Integer(compute="_compute_potential_count", string="Potential")
    x_contract_count = fields.Integer(compute="_compute_contract_count", string="Contracts")
    x_vehicle_management_count = fields.Integer(compute="_compute_vehicle_management_count", string="Vehicle Management")
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
    x_bank_line_ids = fields.One2many('bank.line', 'x_partner_id', string='Bank Lines')
    x_contact_line_ids = fields.One2many('contact.line', 'x_partner_id', string='Contact Lines')

    def _compute_potential_count(self):
        for record in self:
            record.x_potential_count = self.env['crm.lead'].search_count([('x_partner_id', '=', record.id)]) 

    def _compute_contract_count(self):
        for record in self:
            record.x_contract_count = self.env['sale.order'].search_count([('x_cusomer_id', '=', record.id)])

    def _compute_vehicle_management_count(self):
        for record in self:
            record.x_vehicle_management_count = self.env['fleet.vehicle'].search_count([('partner_id', '=', record.id)])

    def action_view_potential(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Potential',
            'view_mode': 'tree,form',
            'res_model': 'crm.lead',
            'domain': [('x_partner_id', '=', self.id)],
            'context': {'default_x_partner_id': self.id},
        }

    def action_view_contracts(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contracts',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('x_partner_id', '=', self.id)],
            'context': {'default_x_partner_id': self.id},
        }

    def action_view_vehicle_management(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicle Management',
            'view_mode': 'tree,form',
            'res_model': 'fleet.vehicle',
            'domain': [('x_partner_id', '=', self.id)],
            'context': {'default_x_partner_id': self.id},
        }

    def action_create_contact(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Contact',
            'res_model': 'contact.line',
            'view_mode': 'form',
            'view_id': False,
            'target': 'new',
            'context': {
                'default_x_partner_id': self.id,
                'default_x_name': self.x_name or "New Contact",
            },
        }