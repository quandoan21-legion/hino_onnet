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
        'owned.team.car.line', 'customer_rank_upgrade_id', string="Owned Vehicle List"
    )
    x_owned_team_car_hino_ids = fields.One2many(
        'owned.team.car.line', 'customer_rank_upgrade_id',
        string='Hino Vehicles', compute='_compute_x_owned_team_car_hino_ids', store=False
    )

    x_owned_team_car_other_ids = fields.One2many(
        'owned.team.car.line', 'customer_rank_upgrade_id',
        string='Other Vehicles', compute='_compute_x_owned_team_car_other_ids', store=False
    )

    model_ids_hino = fields.Many2many('product.product', string='Hino Model IDs', compute='_compute_hino_model_ids',
                                      store=False)
    model_ids_hino_names = fields.Many2many('product.product', string='Hino Model Names',
                                            compute='_compute_hino_model_names', store=False)

    @api.depends('x_owned_team_car_ids')
    def _compute_x_owned_team_car_hino_ids(self):
        for record in self:
            record.x_owned_team_car_hino_ids = record.x_owned_team_car_ids.filtered(lambda c: c.x_is_hino_vehicle)

    @api.depends('x_owned_team_car_ids')
    def _compute_x_owned_team_car_other_ids(self):
        for record in self:
            record.x_owned_team_car_other_ids = record.x_owned_team_car_ids.filtered(lambda c: not c.x_is_hino_vehicle)

    def _get_status_display_name(self, status):
        return STATUS_SELECTION.get(status, status)
    @api.onchange('status')
    def _toggle_readonly_fields(self):
        if self.status == 'draft':
            self.update({
                'x_request_form_code': False,
                'x_partner_id': False,
                'x_currently_rank_id': False,
                'x_rank_upgrade_id': False,
                'x_quantity_of_hino': False,
                'x_total_quantity': False,
            })

    # is_updated = fields.Boolean(string="Data Updated", default=False)
    # can_refuse = fields.Boolean(compute="_compute_can_refuse", store=True)
    # @api.depends('is_updated')
    # def _compute_can_refuse(self):
    #     for record in self:
    #         record.can_refuse = record.is_updated

    @api.depends('x_owned_team_car_ids.x_model_name')
    def _compute_hino_model_names(self):
        for record in self:
            hino_products = self.env['product.product'].search([('name', 'ilike', 'Hino')])
            record.model_ids_hino_names = hino_products

    @api.depends('x_owned_team_car_ids.x_model_name')
    def _compute_hino_model_ids(self):
        for record in self:
            hino_products = self.env['product.product'].search([('name', 'ilike', 'Hino')])
            record.model_ids_hino = hino_products

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
                        f"Quantity of Hino ({record.x_quantity_of_hino}) must from {min_hino} to {max_hino}."
                    )

                if not (min_total <= record.x_total_quantity <= max_total):
                    raise ValidationError(
                        f"Total car ({record.x_total_quantity}) must from {min_total} to {max_total}."
                    )

    @api.depends('x_partner_id')
    def _compute_currently_rank_id(self):
        for record in self:
            record.x_currently_rank_id = record.x_partner_id.x_currently_rank_id if record.x_partner_id else False

    # @api.onchange('x_partner_id')
    # def _onchange_x_partner_id(self):
    #     """ Tự động lấy danh sách xe khi chọn khách hàng """
    #     for record in self:
    #         if record.x_partner_id:
    #             record.x_owned_team_car_ids = [(5, 0, 0)]  # Xóa danh sách cũ
    #             cars = self.env['owned.team.car.line'].search([('x_partner_id', '=', record.x_partner_id.id)])
    #             record.x_owned_team_car_ids = [(4, car.id) for car in cars]
    @api.onchange('x_partner_id')
    def _onchange_x_partner_id(self):
        """Tự động cập nhật số lượng xe khi chọn khách hàng"""
        for record in self:
            if record.x_partner_id:
                record.x_total_quantity = record.x_partner_id.x_number_of_vehicles
                record.x_quantity_of_hino = record.x_partner_id.x_hino_vehicle

    # @api.depends('x_owned_team_car_ids.x_quantity')
    # def _compute_total_quantity(self):
    #     """ Tính tổng số lượng xe từ danh sách x_owned_team_car_ids """
    #     for record in self:
    #         record.x_total_quantity = sum(record.x_owned_team_car_ids.mapped('x_quantity'))
    #
    #
    # @api.depends('x_owned_team_car_ids.x_model_name', 'x_owned_team_car_ids.x_quantity')
    # def _compute_quantity_of_hino(self):
    #     """Tính số lượng xe có x_is_hino = True."""
    #     for record in self:
    #         record.x_quantity_of_hino = sum(
    #             car.x_quantity for car in
    #             record.x_owned_team_car_ids.filtered(lambda c: c.x_model_name and c.x_model_name.x_is_hino)
    #         )
    @api.depends('x_partner_id.x_number_of_vehicles')
    def _compute_total_quantity(self):
        """Lấy tổng số lượng xe từ x_number_of_vehicles của khách hàng"""
        for record in self:
            record.x_total_quantity = record.x_partner_id.x_number_of_vehicles if record.x_partner_id else 0

    @api.depends('x_partner_id.x_hino_vehicle')
    def _compute_quantity_of_hino(self):
        """Lấy số lượng xe Hino từ x_hino_vehicle của khách hàng"""
        for record in self:
            record.x_quantity_of_hino = record.x_partner_id.x_hino_vehicle if record.x_partner_id else 0

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

        return super().create(vals)

    def action_update_data(self):
        self.write({'status': 'draft'})
        # self.write({'is_updated': True})
        for record in self:
            if record.x_partner_id:
                # Clear and update owned vehicle list
                record.x_owned_team_car_ids = [(5, 0, 0)]  # Clear existing data
                cars = self.env['owned.team.car.line'].search([('x_partner_id', '=', record.x_partner_id.id)])
                record.x_owned_team_car_ids = [(4, car.id) for car in cars]

            # Recalculate vehicle-related values
        # record._compute_quantity_of_hino()
        # record._compute_total_quantity()

    def action_submit(self):
        self.write({'status': 'pending'})

    def action_cancel(self):
        """Pop up a form to create an approval history record without customer_rank_upgrade_id."""
        self.ensure_one()

        # Change the status to 'canceled'
        self.write({'status': 'canceled'})

        # Open the approval history form without unwanted fields
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
            'target': 'new',  # Open as a pop-up
        }

    def action_approve(self):
        self.ensure_one()

        # Change the status to 'canceled'
        self.write({'status': 'approved'})
        if self.x_partner_id and self.x_rank_upgrade_id:
            self.x_partner_id.write({'x_currently_rank_id': self.x_rank_upgrade_id.id})

        self.env['approve.history'].create({
            'employee_id': self.env.user.employee_id.id,
            'department_id': self.env.user.employee_id.department_id.id,
            'position_id': self.env.user.employee_id.job_id.id,
            'status_from': self._get_status_display_name(self.status),  # Trạng thái trước khi duyệt
            'status_to': self._get_status_display_name('approved'),  # Trạng thái sau khi duyệt
            'approve_date': fields.Date.today(),
            'customer_rank_upgrade_id': self.id,
            'note': 'Approved by ' + self.env.user.name,  # Ensure a note is set
        })

        return True

    def action_refuse(self):
        self.ensure_one()

        # Change the status to 'canceled'
        self.write({'status': 'rejected'})

        # Return action to open the approval history form for new record creation
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
            'target': 'new',  # Opens as a pop-up
        }

    def action_reset_to_draft(self):
        self.ensure_one()

        # Change the status to 'canceled'
        self.write({'status': 'draft'})

        self.env['approve.history'].create({
            'employee_id': self.env.user.employee_id.id,
            'department_id': self.env.user.employee_id.department_id.id,
            'position_id': self.env.user.employee_id.job_id.id,
            'status_from': self._get_status_display_name(self.status),  # Trạng thái trước khi duyệt
            'status_to': self._get_status_display_name('draft'),  # Trạng thái sau khi duyệt
            'approve_date': fields.Date.today(),
            'customer_rank_upgrade_id': self.id,
            'note': 'Reset to draft by ' + self.env.user.name,
        })

        return True

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._update_partner_rank()
        return record

    def write(self, vals):
        res = super().write(vals)
        self._update_partner_rank()
        return res

    def _update_partner_rank(self):
        for record in self:
            if record.status == 'approved' and record.x_partner_id:
                record.x_partner_id.x_currently_rank_id = record.x_rank_upgrade_id
