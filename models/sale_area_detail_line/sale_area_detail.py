from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SaleAreaDetail(models.Model):
    _name = 'sales.area.detail.line'
    x_sale_area_id = fields.Many2one('sale.area', string='Sales Area')
    x_sale_area_detail = fields.Char(related='x_sale_area_id.x_field_sale_name', string='Sales Area Name', readonly=True)
    x_number = fields.Integer(string='STT', readonly=True, copy=False)   
    x_code = fields.Many2one('res.country.state', string='Code Province', required=False)
    x_name = fields.Many2one('res.country.state',string="Name Province", readonly=True)
