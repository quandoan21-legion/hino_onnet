from odoo import models, fields, api, exceptions 

class SaleArea(models.Model):
    _name = 'sale.area'
    
    x_field_sale_name = fields.Char(string='Sale Name', required=True)
    x_field_sale_code = fields.Char(string='Area Code', required=True, copy=False, default=lambda self: self._generate_sale_code())
    x_is_free_sales_area = fields.Boolean(string='Free Sales Area', required=False)
    x_release_time = fields.Datetime(string='Release Time', required=True)
    x_attach_file = fields.Binary(string='Attach File', required=True)
    
    x_sales_area_detali_ids = fields.One2many('sales.area.detail', 'x_sale_area_id', string='Sales Area Detail')

    @api.model
    def create(self, vals):
        if vals.get('x_is_free_sales_area') and self.search_count([('x_is_free_sales_area', '=', True)]) > 0:
            raise exceptions.ValidationError("Đã tồn tại một khu vực bán hàng miễn phí. Vui lòng cập nhật bản ghi hiện tại.")
        vals.setdefault('x_field_sale_code', self._generate_sale_code())
        return super().create(vals)

    def write(self, vals):
        if vals.get('x_is_free_sales_area') and self.search_count([('x_is_free_sales_area', '=', True)]) > 0:
            raise exceptions.ValidationError("Đã tồn tại một khu vực bán hàng miễn phí. Vui lòng cập nhật bản ghi hiện tại.")
        return super().write(vals)
    
    def _generate_sale_code(self):
        return f'KV{self.env["ir.sequence"].next_by_code("sale.area") or "001"}'
    
    @api.constrains('x_is_free_sales_area')
    def _check_free_sales_area(self):
        if self.x_is_free_sales_area and self.search_count([('x_is_free_sales_area', '=', True), ('id', '!=', self.id)]) > 0:
            raise exceptions.ValidationError(f"{self.x_field_sale_code} - Đã tồn tại một khu vực bán hàng miễn phí. Vui lòng cập nhật bản ghi hiện tại.")

    @api.constrains('x_attach_file_name')
    def _check_file_format(self):
        if self.x_attach_file_name and not self.x_attach_file_name.lower().endswith('.pdf'):
            raise exceptions.ValidationError("Chỉ chấp nhận tệp PDF.")
    