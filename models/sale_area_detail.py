from odoo import models, fields, api

class SaleAreaDetail(models.Model):
    _name = 'sales.area.detail.line'
    
    x_sale_area_id = fields.Many2one('sale.area', string='Sales Area')
    x_number = fields.Integer(string='STT', default=lambda self: self._get_next_sequence(), readonly=True)   
    x_code = fields.Many2one('res.country.state', string='Code Province', required=False)
    x_name = fields.Many2one('res.country.state',string="Name Province", readonly=True)

    
    @api.model
    def _get_next_sequence(self):
        last_record = self.search([], order='x_number desc', limit=1)
        return (last_record.x_number or 0) + 1

    @api.onchange('x_code')
    def _onchange_code(self):
        for record in self:
            record.x_name = record.x_code if record.x_code else False