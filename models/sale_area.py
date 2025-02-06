from odoo import models, fields, api, exceptions 

class SaleArea(models.Model):
    _name = 'sale.area'
    
    x_field_sale_name = fields.Char(string='Sale Name', required=True)
    x_field_sale_code = fields.Char(string='Area Code', required=True, readonly=True, copy=False, default=lambda self: self._generate_sale_code())
    x_is_free_sales_area = fields.Boolean(string='Free Sales Area', required=False)
    x_release_time = fields.Datetime(string='Release Time', required=True)
    x_attach_file = fields.Binary(string='Attach File', required=True)
    
    x_sales_area_detali_ids = fields.One2many('sales.area.detail.line', 'x_sale_area_id', string='Sales Area Detail')

    @api.model
    def create(self, vals):
        if vals.get('x_is_free_sales_area') and self.search_count([('x_is_free_sales_area', '=', True)]) > 0:
            raise exceptions.ValidationError("A free sales area already exists. Please update the existing record.")
        vals.setdefault('x_field_sale_code', self._generate_sale_code())
        return super().create(vals)

    def write(self, vals):
        if vals.get('x_is_free_sales_area') and self.search_count([('x_is_free_sales_area', '=', True)]) > 0:
            raise exceptions.ValidationError("A free sales area already exists. Please update the existing record.")
        return super().write(vals)
    
    def _generate_sale_code(self):
        last_sale_area = self.search([], order='x_field_sale_code desc', limit=1)
        if last_sale_area:
            last_number = int(last_sale_area.x_field_sale_code[2:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f'KV{str(new_number).zfill(3)}'
    
    @api.constrains('x_is_free_sales_area')
    def _check_free_sales_area(self):
        if self.x_is_free_sales_area and self.search_count([('x_is_free_sales_area', '=', True), ('id', '!=', self.id)]) > 0:
            raise exceptions.ValidationError(f"{self.x_field_sale_code} - A free sales area already exists. Please update the existing record.")

    @api.constrains('x_attach_file_name')
    def _check_file_format(self):
        if self.x_attach_file_name and not self.x_attach_file_name.lower().endswith('.pdf'):
            raise exceptions.ValidationError("Only PDF files are allowed.")
    