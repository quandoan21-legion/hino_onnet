from odoo import models, fields, api, exceptions

class SaleAreaMethods(models.Model):
    _inherit = 'sale.area'
    
    # @api.depends('x_field_sale_name')
    # def _compute_display_name(self):
    #     for record in self:
    #         record.display_name = record.x_field_sale_name
    
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