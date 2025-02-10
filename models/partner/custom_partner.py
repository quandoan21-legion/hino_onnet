import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_potential_count = fields.Integer(string="Lead") # x_potential_count = fields.Integer(compute="_compute_potential_count", string="Potential") - Logic
    x_contract_count = fields.Integer(string="Contract") # x_contract_count = fields.Integer(compute="_compute_contract_count", string="Contracts") - Logic
    x_vehicle_management_count = fields.Integer(string="Vehicle Management") # x_vehicle_management_count = fields.Integer(compute="_compute_vehicle_management_count", string="Vehicle Management") - Logic
    company_type = fields.Selection(
            selection_add=[('internal_hmv', 'Internal HMV')],
        )
    x_dealer_id = fields.Char(string='Dealer', readonly=True) # liên quan đến dealer.group - chưa có giải thích cụ thể
    x_dealer_branch_id = fields.Many2one('res.company', string='Dealer Branch', default=lambda self: self.env.company, tracking=True, readonly=True)
    x_customer_type = fields.Selection(
        [('last_customer', 'Last Customer'), ('third_party', 'Third Party'), ('body_maker', 'Body Maker')],
        string='Customer Type', default='last_customer', tracking=True
    )
    x_contact_address = fields.Char(string="Address", store=True)
    x_function = fields.Char(string='Function')
    x_customer_code = fields.Char(string='Customer Code', tracking=True, readonly=True, copy=False)
    x_district = fields.Char(string='District')
    x_state_id = fields.Many2one('res.country.state', string="State/Province")
    x_field_sale_id = fields.Many2one('sale.area',string='Field Sale')
    x_currently_rank_id = fields.Many2one('customer.rank', string='Currently Rank')
    x_business_registration_id = fields.Char(string='Business Registration ID', help='Business Registration ID')
    x_identity_number = fields.Char(string='Identity Number', help='National or Personal Identity Number')
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
    x_owned_car_line_ids = fields.One2many('owned.team.car.line', 'x_partner_id', string='Owned Team Car Lines')
    x_vehicle_images = fields.Binary(attachment=True)

    @api.model
    def create(self, vals):
        if not vals.get('x_customer_code'):
            vals['x_customer_code'] = self.env['ir.sequence'].next_by_code('res.partner.cus_number')
        return super().create(vals)

    # @api.depends('is_company')
    # def _compute_company_type(self):
    #     for partner in self:
    #         if partner.company_type == 'internal_hmv':
    #             continue
    #         partner.company_type = 'company' if partner.is_company else 'person'

    # def _write_company_type(self):
    #     for partner in self:
    #         if partner.company_type == 'internal_hmv':
    #             continue
    #         partner.is_company = partner.company_type == 'company'

    # @api.onchange('company_type')
    # def onchange_company_type(self):
    #     if self.company_type == 'internal_hmv':
    #         return
    #     self.is_company = (self.company_type == 'company')
    

    @api.constrains('x_business_registration_id')
    def _check_business_registration_id(self):
        for record in self:
            if record.x_business_registration_id:
                existing = self.search([
                    ('x_business_registration_id', '=', record.x_business_registration_id),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError("Business Registration ID must be unique.")
        
            if record.x_business_registration_id:
                if not re.fullmatch(r'\d{1,10}', record.x_business_registration_id):
                    raise ValidationError("Business Registration ID must contain only numbers and be at most 10 digits long.")
    
    @api.constrains('x_identity_number')
    def _check_identity_number(self):
        for record in self:
            if record.x_identity_number:
                existing = self.search([
                    ('x_identity_number', '=', record.x_identity_number),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError("The Identity number must be unique.")

            if record.x_identity_number:
                if not re.match(r'^\d{9,12}$', record.x_identity_number):
                    raise ValidationError("The Identity number must contain from 9 to 12 digits.")
    
    @api.constrains('phone', 'mobile')
    def _check_phone_number_format(self):
        for record in self:
            if record.phone and not re.fullmatch(r'0\d{1,10}', record.phone):
                raise ValidationError("Phone number must not more than 10 digits and start with 0.")
            if record.mobile and not re.fullmatch(r'0\d{1,10}', record.mobile):
                raise ValidationError("Mobile number must not more than 10 digits and start with 0.")

    @api.constrains('x_business_registration_id', 'x_customer_type', 'x_register_sale_3rd_id', 'x_identity_number')
    def _check_required_fields(self):
        for record in self:
            if record.company_type == 'internal_hmv':
                continue  
            if not record.is_company and not record.x_identity_number:
                raise ValidationError("Identity Number is required for individuals. Please enter a valid Identity Number.")
            if record.is_company and not record.x_business_registration_id:
                raise ValidationError("Business Registration ID is required for companies. Please enter a valid Business Registration ID.")
            if record.x_customer_type == 'third_party' and not record.x_register_sale_3rd_id:
                raise ValidationError("Register Sale 3rd is required for Third Party customers. Please enter a valid Register Sale 3rd ID.")
    
    # def _compute_potential_count(self):
    #     for record in self:
    #         record.x_potential_count = self.env['crm.lead'].search_count([('x_partner_id', '=', record.id)]) 

    # def _compute_contract_count(self):
    #     for record in self:
    #         record.x_contract_count = self.env['sale.order'].search_count([('x_cusomer_id', '=', record.id)])

    # def _compute_vehicle_management_count(self):
    #     for record in self:
    #         record.x_vehicle_management_count = self.env['fleet.vehicle'].search_count([('partner_id', '=', record.id)])

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
                'default_name': self.x_name or "New Contact",
            },
        }

    def action_upgrade_client(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer Rank',
            'view_mode': 'tree,form',
            'res_model': 'crm.lead', # link đến phần nâng hạng khách hàng hiện tại để crm.lead
        }