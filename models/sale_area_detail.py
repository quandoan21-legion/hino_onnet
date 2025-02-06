from odoo import models, fields, api

class SaleAreaDetail(models.Model):
    _name = 'sales.area.detail.line'
    
    x_sale_area_id = fields.Many2one('sale.area', string='Sales Area')
    x_number = fields.Integer(string='STT', readonly=False)   
    x_code = fields.Many2one('res.country.state', string='Code Province', required=False)
    x_name = fields.Many2one('res.country.state',string="Name Province", readonly=False)

    @api.model
    def create(self, vals):
        sale_area = vals.get('x_sale_area_id')
        if sale_area:
            last_number = self.search([('x_sale_area_id', '=', sale_area)], order='x_number desc', limit=1)
            vals['x_number'] = last_number.x_number + 1 if last_number else 1

        if vals.get('x_code'):
            vals['x_name'] = vals['x_code']
        
        return super(SaleAreaDetail, self).create(vals)

    @api.onchange('x_code')
    def _onchange_code(self):
        for record in self:
            record.x_name = record.x_code if record.x_code else False
    
    @api.onchange('x_sale_area_id')
    def _onchange_sale_area_id(self):
        if self.x_sale_area_id:
            last_number = self.search([('x_sale_area_id', '=', self.x_sale_area_id.id)], order='x_number desc', limit=1)
            self.x_number = last_number.x_number + 1 if last_number else 1

    @api.model
    def default_get(self, fields_list):
        res = super(SaleAreaDetail, self).default_get(fields_list)
        sale_area = res.get('x_sale_area_id')
        if sale_area:
            last_number = self.search([('x_sale_area_id', '=', sale_area)], order='x_number desc', limit=1)
            res['x_number'] = last_number.x_number + 1 if last_number else 1
        return res