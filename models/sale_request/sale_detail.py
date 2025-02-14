from odoo import models, fields

class SaleDetail(models.Model):
    _name = 'sale.detail'
    _description = 'Chi tiết bán hàng'

    x_number = fields.Integer(string='STT', default=1)
    x_customers_use_id = fields.Many2one(
        'res.partner', string='Mã khách hàng', help='Mã khách hàng từ đề nghị bán trái vùng/Bên thứ 3/Nhà đóng thùng'
    )
    x_customers_name = fields.Char(string='Tên khách hàng sử dụng')
    x_identification_card = fields.Many2one('res.partner', string='CCCD/CMND')
    x_specific_address = fields.Char(string='Địa chỉ cụ thể')
    x_province_id = fields.Many2one('res.country.state', string='Tỉnh/Thành phố', required=True)
    x_product_id = fields.Many2one('product.product', string='Model', required=True)
    x_bin_type_id = fields.Many2one('master.data.bin.type', string='Loại thùng', required=True)
    x_quantity = fields.Integer(string='Số lượng', required=True)
    x_quantity_finalize = fields.Integer(string='Số lượng chốt', default=lambda self: self.quantity)
    x_quantity_done = fields.Many2one('retail.sale.detail', string='Số lượng hoàn thành')
    x_note = fields.Char(string='Ghi chú')
    x_attach_file = fields.Binary(string='Đính kèm')

    def action_cancel(self):
        """ Khi nhấn button 'Hủy', cập nhật số lượng chốt thành số lượng hoàn thành """
        for record in self:
            record.x_quantity_finalize = record.x_quantity_done.quantity if record.x_quantity_done else 0
