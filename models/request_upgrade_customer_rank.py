from odoo import models, fields, api

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
        copy=False,
    )
    x_partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True
    )
    x_currently_rank_id = fields.Many2one(
        'customer.rank',
        string='Current Customer Rank',
        readonly=True
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

    @api.model
    def create(self, vals):
        if vals.get('x_request_form_code', 'New') == 'New':
            vals['x_request_form_code'] = self.env['ir.sequence'].next_by_code('customer.rank.upgrade') or '00001'
        return super(CustomerRankUpgrade, self).create(vals)

    def action_update_data(self):
        for record in self:
            record._compute_quantity_of_hino()
            record._compute_total_quantity()

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

    @api.depends('x_partner_id', 'x_owned_team_car_ids')
    def _compute_quantity_of_hino(self):
        for record in self:
            if record.x_partner_id:
                record.x_quantity_of_hino = sum(
                    self.env['owned.team.car.line'].search([
                        ('partner_id', '=', record.x_partner_id.id),
                        ('model_name.name', '=', 'Hino')
                    ]).mapped('quantity')
                )
            else:
                record.x_quantity_of_hino = 0

    @api.depends('x_partner_id', 'x_owned_team_car_ids')
    def _compute_total_quantity(self):
        for record in self:
            if record.x_partner_id:
                record.x_total_quantity = sum(
                    self.env['owned.team.car.line'].search([
                        ('partner_id', '=', record.x_partner_id.id)
                    ]).mapped('quantity')
                )
            else:
                record.x_total_quantity = 0
