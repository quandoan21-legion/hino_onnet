from odoo import models, fields, api
from odoo.exceptions import ValidationError
from lxml import etree
import json


class SaleDetail(models.Model):
    _name = 'sale.detail'
    _description = 'Chi tiết bán hàng'

    x_number = fields.Integer(string='STT',readonly=True)
    x_customers_use_id = fields.Many2one(
        'res.partner', string='Customer use id', help='Mã khách hàng từ đề nghị bán trái vùng/Bên thứ 3/Nhà đóng thùng',

    )
    x_customers_name = fields.Char(string='Customer name')
    # x_customer_name = fields.Char(string='Customer Name')
    x_identification_card = fields.Many2one('res.partner', string='CCCD/CMND')
    x_specific_address = fields.Char(string='Address')
    x_province_id = fields.Many2one('res.country.state', string='Provice', required=True)
    x_product_id = fields.Many2one('product.product', string='Model', required=True)
    x_bin_type_id = fields.Many2one('hino.body.type', string='Bin type id')
    x_quantity = fields.Integer(string='Quantity', required=True)
    x_quantity_finalize = fields.Integer(string='Quantity finalize', default=lambda self: self.x_quantity)
    # x_quantity_done = fields.Many2one('retail.sale.detail', string='Số lượng hoàn thành')
    x_note = fields.Char(string='Note')
    x_attach_file = fields.Binary(string='Attach file')
    sale_request_id = fields.Many2one('sale.request', string='Sale Request')
    x_customer_type = fields.Selection(
        related='sale_request_id.x_customer_type',
        string='Customer Type',
        store=True
    )
    x_state = fields.Selection(
        related='sale_request_id.x_state',
        string='Customer state',
        store=True,
        invisible=True
    )
    x_check = fields.Boolean(string="Check", default=False)
    # def action_cancel(self):
    #     """ Khi nhấn button 'Hủy', cập nhật số lượng chốt thành số lượng hoàn thành """
    #     for record in self:
    #         record.x_quantity_finalize = record.x_quantity_done.quantity if record.x_quantity_done else 0

    @api.model
    def create(self, vals):
        if 'x_number' not in vals or vals['x_number'] <= 0:
            last_record = self.search([], order="x_number desc", limit=1)
            vals['x_number'] = last_record.x_number + 1 if last_record else 1  # Start from 1
        return super(SaleDetail, self).create(vals)

    def action_cancel(self):
        """ Khi nhấn button 'Hủy', cập nhật [Số lượng chốt] = [Số lượng hoàn thành] """
        for record in self:
            record.x_quantity_finalize = record.x_quantity

    def action_delete_line(self):
        """ Chỉ cho phép xóa khi phiếu ở trạng thái Nháp """
        for record in self:
            if record.sale_request_id.x_state == 'draft':
                record.unlink()
            else:
                raise ValidationError("Chỉ có thể xóa sản phẩm khi phiếu ở trạng thái Nháp!")

    @api.onchange('x_customer_type')
    def _onchange_customer_type(self):
        if self.x_customer_type == 'out_of_area':
            self.x_customers_name = False

    @api.depends('x_identification_card')
    def _compute_identification_number(self):
        for record in self:
            record.x_identification_number = record.x_identification_card.x_identity_number if record.x_identification_card else False

    def fields_view_get(self, view_id=None, view_type='tree', toolbar=False, submenu=False):
        """Dynamically hide x_customer_type and x_state columns without removing them."""
        result = super(SaleDetail, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu
        )

        if view_type in ['tree', 'list']:
            doc = etree.fromstring(result['arch'])

            # Add 'invisible' attribute to x_customer_type
            for field in doc.xpath("//field[@name='x_customer_type']"):
                field.set('column_invisible', '1')

            # Add 'invisible' attribute to x_state
            for field in doc.xpath("//field[@name='x_state']"):
                field.set('column_invisible', '1')

            result['arch'] = etree.tostring(doc, encoding='unicode')

        return result