from odoo import models, fields, api, exceptions 

class SaleArea(models.Model):
    _name = 'sale.area'
    _rec_name = 'x_field_sale_name'
    
    x_field_sale_name = fields.Char(string='Sale Name', required=True)
    x_field_sale_code = fields.Char(string='Area Code', required=True, readonly=True, copy=False, default=lambda self: self._generate_sale_code())
    x_is_free_sales_area = fields.Boolean(string='Free Sales Area', required=False)
    x_release_time = fields.Datetime(string='Release Time', required=True)
    x_attach_file = fields.Binary(string='Attach File', required=True)
    
    x_sales_area_detail_ids = fields.One2many('sales.area.detail.line', 'x_sale_area_id', string='Sales Area Detail')

    
    