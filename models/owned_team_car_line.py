from odoo import models, fields, api

class CustomLeadLine(models.Model):
    _name = 'owned.team.car.line'

    lead_id = fields.Many2one('crm.lead', string='Lead')
    x_partner_id = fields.Many2one('res.partner', string='Partner')
    customer_rank_upgrade_id = fields.Many2one('customer.rank.upgrade', string='Khách hàng nâng hạng')
    x_model_name = fields.Char(string='Range of vehicle')
    x_quantity = fields.Integer(string='Number')
    x_brand_name = fields.Char(string='Car Name')
    x_is_hino_vehicle = fields.Boolean(string='Is Hino Vehicle', default=False)
