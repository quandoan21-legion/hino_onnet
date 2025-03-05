from odoo import models, fields, api
from odoo.exceptions import ValidationError

STATUS_SELECTION = {
    'draft': 'Draft',
    'pending': 'Pending Approval',
    'approved': 'Approved',
    'rejected': 'Rejected',
    'canceled': 'Canceled',
}

class CustomerRankUpgrade(models.Model):
    _name = 'customer.rank.upgrade'
    _description = 'Customer Rank Upgrade'
    _rec_name = 'x_request_form_code'

    status = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('canceled', 'Canceled')
    ], string='Status', default='draft', required=True)

    x_request_form_code = fields.Char(
        string='Request Form Code',
        readonly=True,
        copy=False
    )
    x_partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        ondelete='cascade'
    )
    x_currently_rank_id = fields.Many2one(
        'customer.rank',
        string='Current Customer Rank',
        readonly=True,
        compute='_compute_currently_rank_id',
        store=True
    )
    x_rank_upgrade_id = fields.Many2one(
        'customer.rank',
        string='Rank Upgrade'
    )
    x_quantity_of_hino = fields.Integer(
        string='Number of Hino Vehicles',
        compute='_compute_quantity_of_hino',
        store=True
    )
    x_total_quantity = fields.Integer(
        string='Total Number of Vehicles',
        compute='_compute_total_quantity',
        store=True
    )
    approve_history_ids = fields.One2many(
        'approve.history', 'customer_rank_upgrade_id', string="Approval History"
    )
    x_owned_team_car_ids = fields.One2many(
        'owned.team.car.line', 'customer_rank_upgrade_id',
        string="Owned Vehicle List",
        compute='_compute_x_owned_team_car_ids',
        store=True
    )
    x_owned_car_line_ids = fields.One2many(
        'owned.team.car.line', 'x_partner_id',
        string='Owned Vehicle List',
        compute='_compute_x_owned_car_line_ids',
        store=True
    )
    x_is_hino_vehicle = fields.One2many(
        'owned.team.car.line', 'x_partner_id',
        string='Hino Vehicle List',
        compute='_compute_x_is_hino_vehicle',
        store=True
    )
    x_not_is_hino_vehicle = fields.One2many(
        'owned.team.car.line', 'x_partner_id',
        string='Hino Vehicle List',
        compute='_compute_x_not_is_hino_vehicle',
        store=True
    )
    @api.depends('x_partner_id')
    def _compute_x_owned_car_line_ids(self):
        for record in self:
            if record.x_partner_id:
                record.x_owned_car_line_ids = record.x_partner_id.x_owned_car_line_ids
            else:
                record.x_owned_car_line_ids = False

    @api.depends('x_owned_car_line_ids')
    def _compute_x_is_hino_vehicle(self):
        for record in self:
            record.x_is_hino_vehicle = any(car.x_brand_name == "Hino" for car in record.x_owned_car_line_ids)

    @api.depends('x_owned_car_line_ids.x_is_hino_vehicle')
    def _compute_x_not_is_hino_vehicle(self):
        for record in self:
            if record.x_owned_car_line_ids:
                record.x_is_hino_vehicle = record.x_owned_car_line_ids.filtered(
                    lambda car: car.x_is_hino_vehicle == False)
            else:
                record.x_is_hino_vehicle = [(5, 0, 0)]

    @api.depends('x_owned_car_line_ids.x_is_hino_vehicle')
    def _compute_x_is_hino_vehicle(self):
        for record in self:
            if record.x_owned_car_line_ids:
                record.x_is_hino_vehicle = record.x_owned_car_line_ids.filtered(lambda car: car.x_is_hino_vehicle == True)
            else:
                record.x_is_hino_vehicle = [(5, 0, 0)]

    @api.depends('x_partner_id')
    def _compute_x_owned_car_line_ids(self):
        for record in self:
            if record.x_partner_id:
                record.x_owned_car_line_ids = record.x_partner_id.x_owned_car_line_ids
                record.x_owned_team_car_ids = record.x_partner_id.x_owned_car_line_ids
            else:
                record.x_owned_car_line_ids = [(5, 0, 0)]
                record.x_owned_team_car_ids = [(5, 0, 0)]
    # @api.depends('x_partner_id')
    # def _compute_x_owned_car_line_ids(self):
    #     for record in self:
    #         if record.x_partner_id:
    #             record.x_owned_car_line_ids = record.x_partner_id.x_owned_car_line_ids
    #         else:
    #             record.x_owned_car_line_ids = [(5, 0, 0)]

    # @api.depends('x_partner_id')
    # def _compute_x_owned_team_car_ids(self):
    #     """
    #     Fetch all owned team car lines for the selected customer.
    #     The records are searched using x_partner_id.
    #     """
    #     for record in self:
    #         if record.x_partner_id:
    #             owned_cars = self.env['owned.team.car.line'].search([
    #                 ('x_partner_id', '=', record.x_partner_id.id)
    #             ])
    #             record.x_owned_team_car_ids = [(6, 0, owned_cars.ids)]
    #         else:
    #             record.x_owned_team_car_ids = [(5, 0, 0)]

    @api.onchange('x_partner_id')
    def _onchange_x_partner_id(self):
        """Update vehicle quantity fields when the customer changes."""
        for record in self:
            if record.x_partner_id:
                record.x_total_quantity = record.x_partner_id.x_number_of_vehicles
                record.x_quantity_of_hino = record.x_partner_id.x_hino_vehicle
            else:
                record.x_total_quantity = 0
                record.x_quantity_of_hino = 0

    @api.depends('x_partner_id.x_number_of_vehicles')
    def _compute_total_quantity(self):
        """Compute total number of vehicles from the customer's field."""
        for record in self:
            record.x_total_quantity = record.x_partner_id.x_number_of_vehicles if record.x_partner_id else 0

    @api.depends('x_partner_id.x_hino_vehicle')
    def _compute_quantity_of_hino(self):
        """Compute the number of Hino vehicles from the customer's field."""
        for record in self:
            record.x_quantity_of_hino = record.x_partner_id.x_hino_vehicle if record.x_partner_id else 0

    @api.depends('x_partner_id')
    def _compute_currently_rank_id(self):
        for record in self:
            record.x_currently_rank_id = record.x_partner_id.x_currently_rank_id if record.x_partner_id else False

    def _get_status_display_name(self, status):
        return STATUS_SELECTION.get(status, status)

    @api.constrains('x_quantity_of_hino', 'x_total_quantity', 'x_rank_upgrade_id')
    def _check_vehicle_count(self):
        for record in self:
            if record.x_rank_upgrade_id:
                min_hino = record.x_rank_upgrade_id.min_hino_vehicles
                max_hino = record.x_rank_upgrade_id.max_hino_vehicles
                min_total = record.x_rank_upgrade_id.min_owned_vehicles
                max_total = record.x_rank_upgrade_id.max_owned_vehicles

                if not (min_hino <= record.x_quantity_of_hino <= max_hino):
                    raise ValidationError(
                        f"Quantity of Hino ({record.x_quantity_of_hino}) must be between {min_hino} and {max_hino}."
                    )
                if not (min_total <= record.x_total_quantity <= max_total):
                    raise ValidationError(
                        f"Total vehicles ({record.x_total_quantity}) must be between {min_total} and {max_total}."
                    )

    def action_update_data(self):
        self.write({'status': 'draft'})
        for record in self:
            if record.x_partner_id:
                # Clear and update owned vehicle list
                record.x_owned_team_car_ids = [(5, 0, 0)]
                cars = self.env['owned.team.car.line'].search([
                    ('x_partner_id', '=', record.x_partner_id.id)
                ])
                record.x_owned_team_car_ids = [(4, car.id) for car in cars]

    def action_submit(self):
        self.write({'status': 'pending'})

    def action_cancel(self):
        self.ensure_one()
        self.write({'status': 'canceled'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Approval History',
            'res_model': 'approve.history',
            'view_mode': 'form',
            'context': {
                'default_employee_id': self.env.user.employee_id.id,
                'default_department_id': self.env.user.employee_id.department_id.id,
                'default_position_id': self.env.user.employee_id.job_id.id,
                'default_status_from': self._get_status_display_name(self.status),
                'default_status_to': self._get_status_display_name('canceled'),
                'default_approve_date': fields.Datetime.now(),
                'default_customer_rank_upgrade_id': self.id,
            },
            'target': 'new',
        }

    def action_approve(self):
        self.ensure_one()
        self.write({'status': 'approved'})
        if self.x_partner_id and self.x_rank_upgrade_id:
            self.x_partner_id.write({'x_currently_rank_id': self.x_rank_upgrade_id.id})
        self.env['approve.history'].create({
            'employee_id': self.env.user.employee_id.id,
            'department_id': self.env.user.employee_id.department_id.id,
            'position_id': self.env.user.employee_id.job_id.id,
            'status_from': self._get_status_display_name(self.status),
            'status_to': self._get_status_display_name('approved'),
            'approve_date': fields.Date.today(),
            'customer_rank_upgrade_id': self.id,
            'note': 'Approved by ' + self.env.user.name,
        })
        return True

    def action_refuse(self):
        self.ensure_one()
        self.write({'status': 'rejected'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Approval History',
            'res_model': 'approve.history',
            'view_mode': 'form',
            'context': {
                'default_employee_id': self.env.user.employee_id.id,
                'default_department_id': self.env.user.employee_id.department_id.id,
                'default_position_id': self.env.user.employee_id.job_id.id,
                'default_status_from': self._get_status_display_name('pending'),
                'default_status_to': self._get_status_display_name('rejected'),
                'default_approve_date': fields.Datetime.now(),
                'default_customer_rank_upgrade_id': self.id,
                'note': 'Reset to draft by ' + self.env.user.name,
            },
            'target': 'new',
        }

    def action_reset_to_draft(self):
        self.ensure_one()
        self.write({'status': 'draft'})
        self.env['approve.history'].create({
            'employee_id': self.env.user.employee_id.id,
            'department_id': self.env.user.employee_id.department_id.id,
            'position_id': self.env.user.employee_id.job_id.id,
            'status_from': self._get_status_display_name(self.status),
            'status_to': self._get_status_display_name('draft'),
            'approve_date': fields.Date.today(),
            'customer_rank_upgrade_id': self.id,
            'note': 'Reset to draft by ' + self.env.user.name,
        })
        return True

    @api.model
    def create(self, vals):
        if vals.get('x_request_form_code', 'New') == 'New':
            existing_codes = self.search([], order='x_request_form_code desc', limit=1).mapped('x_request_form_code')
            if existing_codes:
                next_number = str(int(existing_codes[0]) + 1).zfill(5)
            else:
                next_number = '00001'
            while self.search_count([('x_request_form_code', '=', next_number)]) > 0:
                next_number = str(int(next_number) + 1).zfill(5)
            vals['x_request_form_code'] = next_number
        record = super(CustomerRankUpgrade, self).create(vals)
        record._update_partner_rank()
        return record

    def write(self, vals):
        res = super(CustomerRankUpgrade, self).write(vals)
        self._update_partner_rank()
        return res

    def _update_partner_rank(self):
        for record in self:
            if record.status == 'approved' and record.x_partner_id:
                record.x_partner_id.x_currently_rank_id = record.x_rank_upgrade_id
