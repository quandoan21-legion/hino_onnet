# from odoo import models, fields, api
# from odoo.exceptions import ValidationError
#
# class CustomerRankUpgrade(models.Model):
#     _name = 'customer.rank.upgrade'
#     _description = 'Customer Rank Upgrade'
#     _rec_name = 'x_request_form_code'
#
#     status = fields.Selection([
#         ('draft', 'Draft'),
#         ('pending', 'Pending Approval'),
#         ('approved', 'Approved'),
#         ('rejected', 'Rejected'),
#         ('canceled', 'Canceled')
#     ], string='Status', default='draft', required=True)
#
#     x_request_form_code = fields.Char(
#         string='Request Form Code',
#         readonly=True,
#         copy=False
#     )
#     x_partner_id = fields.Many2one(
#         'crm.lead',
#         string='Customer',
#         required=True,
#         ondelete='cascade'
#     )
#     x_currently_rank_id = fields.Many2one(
#         'customer.rank',
#         string='Current Customer Rank',
#         readonly=True,
#         compute='_compute_currently_rank_id',
#         store=True
#     )
#     x_rank_upgrade_id = fields.Many2one(
#         'customer.rank',
#         string='Rank Upgrade'
#     )
#     x_quantity_of_hino = fields.Integer(
#         string='Number of Hino Vehicles',
#         compute='_compute_quantity_of_hino',
#         store=True
#     )
#     x_total_quantity = fields.Integer(
#         string='Total Number of Vehicles',
#         compute='_compute_total_quantity',
#         store=True
#     )
#     approve_history_ids = fields.One2many(
#         'approve.history', 'customer_rank_upgrade_id', string="Approval History"
#     )
#     x_owned_team_car_ids = fields.One2many(
#         'owned.team.car.line', 'customer_rank_upgrade_id', string="Owned Vehicle List"
#     )
#
#     model_ids_hino = fields.Many2many('product.product', string='Hino Model IDs', compute='_compute_hino_model_ids',
#                                       store=False)
#     model_ids_hino_names = fields.Many2many('product.product', string='Hino Model Names',
#                                             compute='_compute_hino_model_names', store=False)
#
#     @api.depends('x_owned_team_car_ids.x_model_name')
#     def _compute_hino_model_names(self):
#         for record in self:
#             hino_products = self.env['product.product'].search([('name', 'ilike', 'Hino')])
#             record.model_ids_hino_names = hino_products
#
#     @api.depends('x_owned_team_car_ids.x_model_name')
#     def _compute_hino_model_ids(self):
#         for record in self:
#             hino_products = self.env['product.product'].search([('name', 'ilike', 'Hino')])
#             record.model_ids_hino = hino_products  # Đảm bảo đây là tập hợp bản ghi, không phải danh sách ID
#
#     @api.constrains('x_quantity_of_hino', 'x_total_quantity', 'x_rank_upgrade_id')
#     def _check_vehicle_count(self):
#         for record in self:
#             if record.x_rank_upgrade_id:
#                 min_hino = record.x_rank_upgrade_id.min_hino_vehicles
#                 max_hino = record.x_rank_upgrade_id.max_hino_vehicles
#                 min_total = record.x_rank_upgrade_id.min_owned_vehicles
#                 max_total = record.x_rank_upgrade_id.max_owned_vehicles
#
#                 if not (min_hino <= record.x_quantity_of_hino <= max_hino):
#                     raise ValidationError(
#                         f"Số lượng xe Hino ({record.x_quantity_of_hino}) phải nằm trong khoảng từ {min_hino} đến {max_hino}."
#                     )
#
#                 if not (min_total <= record.x_total_quantity <= max_total):
#                     raise ValidationError(
#                         f"Tổng số xe ({record.x_total_quantity}) phải nằm trong khoảng từ {min_total} đến {max_total}."
#                     )
#
#     @api.depends('x_partner_id')
#     def _compute_currently_rank_id(self):
#         for record in self:
#             record.x_currently_rank_id = record.x_partner_id.x_partner_rank_id if record.x_partner_id else False
#
#     @api.onchange('x_partner_id')
#     def _onchange_x_partner_id(self):
#         """ Tự động lấy danh sách xe khi chọn khách hàng """
#         for record in self:
#             if record.x_partner_id:
#                 record.x_owned_team_car_ids = [(5, 0, 0)]  # Xóa danh sách cũ
#                 cars = self.env['owned.team.car.line'].search([('lead_id', '=', record.x_partner_id.id)])
#                 record.x_owned_team_car_ids = [(4, car.id) for car in cars]
#
#     @api.depends('x_owned_team_car_ids.x_quantity')
#     def _compute_total_quantity(self):
#         """ Tính tổng số lượng xe từ danh sách x_owned_team_car_ids """
#         for record in self:
#             record.x_total_quantity = sum(record.x_owned_team_car_ids.mapped('x_quantity'))
#
#     @api.depends('x_owned_team_car_ids.x_model_name', 'x_owned_team_car_ids.x_quantity')
#     def _compute_quantity_of_hino(self):
#         """Tính số lượng xe có model_name chứa 'hino'."""
#         for record in self:
#             record.x_quantity_of_hino = sum(
#                 car.x_quantity for car in record.x_owned_team_car_ids.filtered(lambda c: c.x_model_name and 'hino' in c.x_model_name.name.lower())
#             )
#
#     @api.model
#     def create(self, vals):
#         if vals.get('x_request_form_code', 'New') == 'New':
#             vals['x_request_form_code'] = self.env['ir.sequence'].next_by_code('customer.rank.upgrade') or '00001'
#         return super().create(vals)
#
#     def action_update_data(self):
#         self._compute_quantity_of_hino()
#         self._compute_total_quantity()
#
#     def action_submit(self):
#         self.write({'status': 'pending'})
#
#     def action_cancel(self):
#         self.write({'status': 'canceled'})
#
#     def action_approve(self):
#         self.write({'status': 'approved'})
#
#     def action_refuse(self):
#         self.write({'status': 'rejected'})
#
#     def action_reset_to_draft(self):
#         self.write({'status': 'draft'})


from odoo import models, fields, api
from odoo.exceptions import ValidationError

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
        'res.partner',  # Thay đổi từ crm.lead thành res.partner
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

    model_ids_hino = fields.Many2many('product.product', string='Hino Model IDs', compute='_compute_hino_model_ids',
                                      store=False)
    model_ids_hino_names = fields.Many2many('product.product', string='Hino Model Names',
                                            compute='_compute_hino_model_names', store=False)

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
                        f"Số lượng xe Hino ({record.x_quantity_of_hino}) phải nằm trong khoảng từ {min_hino} đến {max_hino}."
                    )

                if not (min_total <= record.x_total_quantity <= max_total):
                    raise ValidationError(
                        f"Tổng số xe ({record.x_total_quantity}) phải nằm trong khoảng từ {min_total} đến {max_total}."
                    )

    @api.depends('x_partner_id')
    def _compute_currently_rank_id(self):
        for record in self:
            record.x_currently_rank_id = record.x_partner_id.x_currently_rank_id if record.x_partner_id else False

    @api.onchange('x_partner_id')
    def _onchange_x_partner_id(self):
        """ Tự động lấy danh sách xe khi chọn khách hàng """
        for record in self:
            if record.x_partner_id:
                record.x_owned_team_car_ids = [(5, 0, 0)]  # Xóa danh sách cũ
                cars = self.env['owned.team.car.line'].search([('x_partner_id', '=', record.x_partner_id.id)])
                record.x_owned_team_car_ids = [(4, car.id) for car in cars]

    @api.depends('x_owned_team_car_ids.x_quantity')
    def _compute_total_quantity(self):
        """ Tính tổng số lượng xe từ danh sách x_owned_team_car_ids """
        for record in self:
            record.x_total_quantity = sum(record.x_owned_team_car_ids.mapped('x_quantity'))

    # @api.depends('x_owned_team_car_ids.x_model_name', 'x_owned_team_car_ids.x_quantity')
    # def _compute_quantity_of_hino(self):
    #     """Tính số lượng xe có model_name chứa 'hino'."""
    #     for record in self:
    #         record.x_quantity_of_hino = sum(
    #             car.x_quantity for car in record.x_owned_team_car_ids.filtered(lambda c: c.x_model_name and 'hino' in c.x_model_name.name.lower())
    #         )
    @api.depends('x_owned_team_car_ids.x_model_name', 'x_owned_team_car_ids.x_quantity')
    def _compute_quantity_of_hino(self):
        """Tính số lượng xe có x_is_hino = True."""
        for record in self:
            record.x_quantity_of_hino = sum(
                car.x_quantity for car in
                record.x_owned_team_car_ids.filtered(lambda c: c.x_model_name and c.x_model_name.x_is_hino)
            )

    @api.model
    def create(self, vals):
        if vals.get('x_request_form_code', 'New') == 'New':
            vals['x_request_form_code'] = self.env['ir.sequence'].next_by_code('customer.rank.upgrade') or '00001'
        return super().create(vals)

    def action_update_data(self):
        self._compute_quantity_of_hino()
        self._compute_total_quantity()

    def action_submit(self):
        self.write({'status': 'pending'})

    def action_cancel(self):
        self.write({'status': 'canceled'})
    def action_approve(self):
        self.write({'status': 'approved'})

    def action_refuse(self):
        self.write({'status': 'rejected'})

    def action_reset_to_draft(self):
        self.write({'status': 'draft'})
