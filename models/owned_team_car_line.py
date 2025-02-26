from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CustomLeadLine(models.Model):
    _name = 'owned.team.car.line'

    lead_id = fields.Many2one('crm.lead', string='Lead')
    x_partner_id = fields.Many2one('res.partner', string='Partner')
    x_model_name = fields.Char(string='Model Name')
    x_model_id = fields.Many2one('product.product', string='Model Hino')
    x_quantity = fields.Integer(string='Quantity')
    x_hino_quantity = fields.Integer(string='Hino Quantity')
    x_brand_name = fields.Char(string='Brand Name')
    x_is_hino_vehicle = fields.Boolean(
        string='Is Hino Vehicle',

        store=True,

    )
    x_brand_car = fields.Char(string='Car Firm Name')
    customer_rank_upgrade_id = fields.Many2one('customer.rank.upgrade', string='Potential customer')

    # @api.depends('x_model_id')
    # def _compute_x_is_hino_vehicle(self):
    #     """Tự động lấy giá trị x_is_hino từ product.product"""
    #     for record in self:
    #         record.x_is_hino_vehicle = record.x_model_id.x_is_hino if record.x_model_id else False

    def create(self, vals_list):
        for vals in vals_list:
            lead = self.env['crm.lead'].browse(vals.get('lead_id'))
            if lead and lead.x_status != "draft":
                raise ValidationError(
                    "You cannot create a new Owned car line because this lead form is not in DRAFT status."
                )
        return super(CustomLeadLine, self).create(vals_list)  # Use 'create', not 'write'

