from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    contract_detail_id = fields.Many2one(
        'crm.contract.line', 
        string="Chi tiết hợp đồng",
        compute="_compute_contract_detail",
        store=True
    )

    @api.depends('order_line')
    def _compute_contract_detail(self):
        for order in self:
            so_lines = order.order_line.mapped('id')
            contract_line = self.env['crm.contract.line'].search([('line_retail_coupon', 'in', so_lines)], limit=1)
            order.contract_detail_id = contract_line if contract_line else False
