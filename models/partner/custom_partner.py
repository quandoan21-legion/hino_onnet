import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_potential_count = fields.Integer(compute="_compute_potential_count", string="Lead")
    x_contract_count = fields.Integer(compute="_compute_contract_count",string="Contract")
    # x_vehicle_management_count = fields.Integer(compute="_compute_vehicle_management_count", string="Vehicle Management") - Logic
    x_vehicle_management_count = fields.Integer(string="Vehicle Management")
    company_type = fields.Selection(
        selection_add=[('internal_hmv', 'Internal HMV')],
    )
    # liên quan đến dealer.group - chưa có giải thích cụ thể
    x_dealer_id = fields.Char(string='Dealer', readonly=True)
    x_dealer_branch_id = fields.Many2one(
        'res.company', string='Dealer Branch', default=lambda self: self.env.company, tracking=True, readonly=True)
    x_customer_type = fields.Selection(
        [('last_customer', 'Last Customer'), ('third_party',
                                              'Third Party'), ('body_maker', 'Body Maker')],
        string='Customer Type', default='last_customer', tracking=True
    )
    x_name = fields.Char(string='Name', tracking=True)
    x_contact_address = fields.Char(string="Address", store=True)
    x_function = fields.Char(string='Function')
    x_customer_code = fields.Char(
        string='Customer Code', tracking=True, readonly=True, copy=False)
    x_district = fields.Char(string='District')
    x_state_id = fields.Many2one('res.country.state', string="State/Province")
    x_field_sale_id = fields.Many2one('sale.area', string='Field Sale')
    x_currently_rank_id = fields.Many2one(
        'customer.rank', string='Currently Rank')
    x_business_registration_id = fields.Char(
        string='Business Registration ID', help='Business Registration ID')
    x_identity_number = fields.Char(
        string='Identity Number', help='National or Personal Identity Number')
    x_industry_id = fields.Many2one(
        'res.partner.industry', string='Industry', tracking=True)
    x_activity_area = fields.Char(string='Activity Area', tracking=True)
    x_service_contract = fields.Boolean(
        string='Service Contact', tracking=True)

    x_number_of_vehicles = fields.Integer(
        string='Number of Vehicles', compute="_compute_number_of_vehicles")
    x_hino_vehicle = fields.Integer(
        string='Hino Vehicle', compute="_compute_number_of_vehicles")
    x_allow_dealer_id = fields.Many2many(
        'res.company', string="Dealers allowed to sale with this customer", readonly=1)
    x_number_repair_order = fields.Integer(string='Number of Repair Order')
    x_cumulative_points = fields.Integer(string='Cumulative Points')
    x_register_sale_3rd_id = fields.Many2one(
        'third.party.registration', string='Register Sale 3rd')
    x_bank_line_ids = fields.One2many(
        'bank.line', 'x_partner_id', string='Bank Lines')
    x_contact_line_ids = fields.One2many(
        'contact.line', 'x_partner_id', string='Contact Lines')
    x_lead_id = fields.Integer(string="lead id")
    x_owned_car_line_ids = fields.One2many(
        'owned.team.car.line', 'x_partner_id', string='Owned Team Car Lines', compute='_compute_owned_car_line_ids')
    x_vehicle_images = fields.Binary(attachment=True)
    # x_owned_car_line_ids = fields.One2many(
    #     'owned.team.car.line', 'x_partner_id', string='Owned Team Car Lines'
    # )
    car_line_ids = fields.One2many(
        'owned.team.car.line', 'partner_id',
        string='Owned Car Lines',

    )
    x_hino_owned_cars = fields.One2many(
        'owned.team.car.line', 'x_partner_id',
        string='Hino Vehicles',
        compute="_compute_hino_and_non_hino_cars",
        store=True
    )

    x_non_hino_owned_cars = fields.One2many(
        'owned.team.car.line', 'x_partner_id',
        string='Non-Hino Vehicles',
        compute="_compute_hino_and_non_hino_cars",
        store=True
    )
    x_owned_car_ids = fields.One2many('owned.team.car.line', 'x_partner_id', string="Owned Cars")

    has_hino_vehicle = fields.Boolean(
        string="Has Hino Vehicle",
        compute="_compute_has_hino_vehicle",
        store=True
    )

    # @api.depends('id')
    # def _compute_owned_car_line_ids(self):
    #     for record in self:
    #         if record.id:
    #             record.x_owned_car_line_ids = self.env['owned.team.car.line'].search([('x_partner_id', '=', record.id)])
    #         else:
    #             record.x_owned_car_line_ids = self.env['owned.team.car.line']

    def _compute_has_hino_vehicle(self):
        for partner in self:
            partner.has_hino_vehicle = bool(
                self.env['owned.team.car.line'].search_count([
                    ('partner_id', '=', partner.id),
                    ('x_is_hino_vehicle', '=', True)
                ])
            )
    @api.depends('x_owned_car_ids.x_is_hino_vehicle')
    def _compute_hino_and_non_hino_cars(self):
        for partner in self:
            hino_vehicles = partner.x_owned_car_ids.filtered(lambda car: car.x_is_hino_vehicle)
            non_hino_vehicles = partner.x_owned_car_ids.filtered(lambda car: not car.x_is_hino_vehicle)
            partner.x_hino_owned_cars = [(6, 0, hino_vehicles.ids)]
            partner.x_non_hino_owned_cars = [(6, 0, non_hino_vehicles.ids)]

    @api.depends('x_number_of_vehicles', 'x_hino_vehicle')
    def _compute_number_of_vehicles(self):
        for record in self:
            if record.x_lead_id:
                record.x_number_of_vehicles = self.env['owned.team.car.line'].read_group(
                    [('lead_id', '=', record.x_lead_id)],
                    ['x_quantity:sum'],
                    []
                )[0]['x_quantity']
                record.x_hino_vehicle = self.env['owned.team.car.line'].read_group(
                    [('lead_id', '=', record.x_lead_id),
                     ('x_is_hino_vehicle', '=', True)],
                    ['x_quantity:sum'],
                    []
                )[0]['x_quantity']
            else:
                record.x_number_of_vehicles = 0
                record.x_hino_vehicle = 0

    @api.depends('x_lead_id')
    def _compute_owned_car_line_ids(self):
        for partner in self:
            if partner.x_lead_id:
                partner.x_owned_car_line_ids = self.env['owned.team.car.line'].search(
                    [('lead_id', '=', partner.x_lead_id)])
            else:
                partner.x_owned_car_line_ids = self.env['owned.team.car.line']

    @api.constrains('phone')
    def _check_phone_unique(self):
        for record in self:
            if record.phone:
                existing = self.search([
                    ('phone', '=', record.phone),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError("Phone number must be unique.")

    @api.model
    def create(self, vals):
        if not vals.get('x_customer_code'):
            vals['x_customer_code'] = self.env['ir.sequence'].next_by_code('res.partner.cus_number')
        return super().create(vals)

    @api.depends('is_company')
    def _compute_company_type(self):
        for partner in self:
            if partner.company_type == 'internal_hmv':
                continue
            partner.company_type = 'company' if partner.is_company else 'person'

    def _write_company_type(self):
        for partner in self:
            if partner.company_type == 'internal_hmv':
                continue
            partner.is_company = partner.company_type == 'company'

    @api.onchange('company_type')
    def onchange_company_type(self):
        if self.company_type == 'internal_hmv':
            return
        self.is_company = (self.company_type == 'company')

    @api.constrains('x_business_registration_id')
    def _check_business_registration_id(self):
        for record in self:
            if record.x_business_registration_id:
                existing = self.search([
                    ('x_business_registration_id', '=',
                     record.x_business_registration_id),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(
                        "Business Registration ID must be unique.")

            if record.x_business_registration_id:
                if not re.fullmatch(r'^\d{1,10}$', record.x_business_registration_id):
                    raise ValidationError(
                        "Business Registration ID must contain only numbers and be at most 10 digits long.")

    @api.constrains('x_identity_number')
    def _check_identity_number(self):
        for record in self:
            if record.x_identity_number:
                existing = self.search([
                    ('x_identity_number', '=', record.x_identity_number),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(
                        "The Identity number must be unique.")

            if record.x_identity_number:
                if not re.match(r'^\d{9,12}$', record.x_identity_number):
                    raise ValidationError(
                        "The Identity number must contain from 9 to 12 digits.")

    @api.constrains('phone', 'mobile')
    def _check_phone_number_format(self):
        for record in self:
            if record.phone and not re.fullmatch(r'0\d{1,9}', record.phone):
                raise ValidationError(
                    "Phone number must not more than 10 digits and start with 0.")
            if record.mobile and not re.fullmatch(r'0\d{1,9}', record.mobile):
                raise ValidationError(
                    "Mobile number must not more than 10 digits and start with 0.")

    # @api.constrains('x_business_registration_id', 'x_customer_type', 'x_register_sale_3rd_id', 'x_identity_number')
    # def _check_required_fields(self):
    #     for record in self:
    #         if record.company_type == 'internal_hmv':
    #             continue
    #         if not record.is_company and not record.x_identity_number:
    #             raise ValidationError("Identity Number is required for individuals. Please enter a valid Identity Number.")
    #         if record.is_company and not record.x_business_registration_id:
    #             raise ValidationError("Business Registration ID is required for companies. Please enter a valid Business Registration ID.")
    #         if record.x_customer_type == 'third_party' and not record.x_register_sale_3rd_id:
    #             raise ValidationError("Register Sale 3rd is required for Third Party customers. Please enter a valid Register Sale 3rd ID.")

    @api.depends('x_lead_id')
    def _compute_potential_count(self):
        for record in self:
            record.x_potential_count = self.env['crm.lead'].search_count([('x_partner_id', '=', record.id)])

    @api.depends('x_lead_id')
    def _compute_contract_count(self):
        for record in self:
            record.x_contract_count = self.env['crm.contract'].search_count([('customer_id', '=', record.id)])

    # def _compute_vehicle_management_count(self):
    #     for record in self:
    #         record.x_vehicle_management_count = self.env['fleet.vehicle'].search_count([('partner_id', '=', record.id)])

    def action_view_potential(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Leads',
            'view_mode': 'tree,form',
            'res_model': 'crm.lead',
            'domain': [('x_partner_id', '=', self.id)],
            'context': {'default_x_partner_id': self.id},
            'views': [(self.env.ref('hino_onnet.customlead_view_tree').id, 'tree'), (False, 'form')],
        }

    def action_view_contracts(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contracts',
            'view_mode': 'tree,form',
            'res_model': 'crm.contract',
            'domain': [('customer_id', '=', self.id)],
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
        self.ensure_one()  # Ensure we are working with a single record

        new_record = self.env['customer.rank.upgrade'].create({
            'x_partner_id': self.id,  # Correctly assign the partner
            'x_currently_rank_id': self.x_currently_rank_id.id if self.x_currently_rank_id else False,
            'x_total_quantity': self.x_number_of_vehicles,
            'x_quantity_of_hino': self.x_hino_vehicle,
        })

        # Fetch the owned vehicles correctly using the partner ID
        owned_cars = self.env['owned.team.car.line'].search([('x_partner_id', '=', self.id)])

        if owned_cars:
            new_record.write({'x_owned_team_car_ids': [(6, 0, owned_cars.ids)]})

        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer Rank Upgrade',
            'view_mode': 'form',
            'res_model': 'customer.rank.upgrade',
<<<<<<< HEAD
            'res_id': new_record.id,
            'target': 'current',
        }
        # self.ensure_one()
        #
        # if self._name != 'res.partner':
        #     raise ValidationError("This action must be performed on a customer (res.partner), not a rank upgrade.")
        #
        # # Create the rank upgrade record
        # new_record = self.env['customer.rank.upgrade'].create({
        #     'x_partner_id': self.id,
        #     'x_currently_rank_id': self.x_currently_rank_id.id if self.x_currently_rank_id else False,
        #     'x_total_quantity': self.x_number_of_vehicles,
        #     'x_quantity_of_hino': self.x_hino_vehicle,
        # })
        #
        # # Auto-fill `owned.team.car.line` if it doesn't exist
        # existing_cars = self.env['owned.team.car.line'].search([
        #     ('x_partner_id', '=', self.id)
        # ])
        #
        # if not existing_cars:
        #     for _ in range(self.x_number_of_vehicles):  # Number of vehicles
        #         self.env['owned.team.car.line'].create({
        #             'x_partner_id': self.id,
        #             'x_model_name': f"Model {_ +1}",  # Replace 'name' with a valid field
        #             'x_quantity': 1,  # Default to 1, adjust as needed
        #             'x_brand_name': "Unknown",  # Provide a default value
        #         })
        #
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Customer Rank',
        #     'view_mode': 'form',
        #     'res_model': 'customer.rank.upgrade',
        #     'res_id': new_record.id,
        #     'target': 'current',
        # }


    @api.onchange('car_line_ids')
    def _onchange_car_line_ids(self):
        """Synchronize x_owned_car_line_ids with car_line_ids when modified"""
        for partner in self:
            partner.x_owned_car_line_ids = partner.car_line_ids

    @api.onchange('x_owned_car_line_ids')
    def _onchange_x_owned_car_line_ids(self):
        """Ensure car_line_ids matches x_owned_car_line_ids when modified"""
        for partner in self:
            partner.car_line_ids = partner.x_owned_car_line_ids

    def _sync_owned_car_lines(self):
        """Ensure partner car lines match with related leads"""
        for partner in self:
            lead_lines = self.env['owned.team.car.line'].search([('lead_id.partner_id', '=', partner.id)])
            partner.x_owned_car_line_ids = [(6, 0, lead_lines.ids)]
            partner.car_line_ids = [(6, 0, lead_lines.ids)]
=======
        }
>>>>>>> 364c512d621b437a83b68a29f02d961a6046a515
