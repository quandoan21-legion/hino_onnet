from odoo import models, fields, api

class CustomLeadLine(models.Model):
    _name = 'owned.team.car.line'

    lead_id = fields.Many2one('crm.lead', string='Lead')
    x_partner_id = fields.Many2one('res.partner', string='Partner')


    x_model_name = fields.Many2one('product.product', string='Range of vehicle')
    x_quantity = fields.Integer(string='Number')
    x_brand_name = fields.Char(string='Car Name')
    x_is_hino_vehicle = fields.Boolean(
        string='Is Hino Vehicle',
        related='x_model_name.x_is_hino',
        store=True,
        readonly=True
    )
    # model_name = fields.Char(string='Range of vehicle')
    # model_name = fields.Many2one('product.product', string='Range of vehicle')
    # quantity = fields.Integer(string='Number')
    x_brand_car = fields.Char(string='Car Firm Name')

    customer_rank_upgrade_id = fields.Many2one('customer.rank.upgrade', string='Potential customer')
    # x_hino_vehicles = fields.One2many(
    #     "owned.team.car.line",
    #     "customer_rank_upgrade_id",
    #     string="Hino Vehicles",
    #     domain=[('x_is_hino_vehicle', '=', True)]
    # )
    #
    # x_other_vehicles = fields.One2many(
    #     "owned.team.car.line",
    #     "customer_rank_upgrade_id",
    #     string="Other Vehicles",
    #     domain=[('x_is_hino_vehicle', '=', False)]
    # )
    @api.depends('x_model_name')
    def _compute_x_is_hino_vehicle(self):
        """Tự động lấy giá trị x_is_hino từ product.product"""
        for record in self:
            record.x_is_hino_vehicle = record.x_model_name.x_is_hino if record.x_model_name else False