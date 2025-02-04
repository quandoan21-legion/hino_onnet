from odoo import models, fields, api
from odoo.exceptions import ValidationError

class VehicleInterest(models.Model):
    _name = 'crm.lead.vehicle.interest.line'

    lead_id = fields.Many2one('crm.lead', string='Cơ hội bán hàng')
    # x_partner_name = fields.Many2one('res.partner', string='Mã KH cuối', required=True)
    x_customer = fields.Char(string='Khách hàng')
    x_address = fields.Text(string='Địa chỉ', required=True)
    # x_province_id = fields.Many2one('res.country.state', string='Tỉnh/Thành phố', required=True)
    # x_order_detail_3rd = fields.Many2one('order.detail.3rd', string='Chi tiết mã đề nghị bán trái vùng')
    # x_model_type_id = fields.Many2one('product.product', string='Loại xe', required=True)
    # x_body_type_id = fields.Many2one('product.body.type', string='Loại thùng', required=True)
    x_quantity = fields.Integer(string='Số lượng', required=True)
    x_expected_implementation_time = fields.Date(string='Ngày giao dự kiến', required=True)
    x_expected_time_sign_contract = fields.Date(string='Ngày ký hợp đồng dự kiến', required=True)
    x_note = fields.Text(string='Ghi chú')
    
    @api.onchange('x_order_detail_3rd', 'x_partner_name')
    def _onchange_x_order_detail_3rd(self):
        if self.x_order_detail_3rd:
            self.x_partner_name = self.x_order_detail_3rd.partner_id
    
    def _onchange_x_order_detail_3rd_data(self):
        if self.x_order_detail_3rd:
            self.x_partner_name = self.x_order_detail_3rd.partner_id
            self.x_customer = self.x_order_detail_3rd.partner_id.name
            self.x_address = self.x_order_detail_3rd.partner_id.street
            self.x_province_id = self.x_order_detail_3rd.partner_id.state_id 
    
    def _onchange_x_order_detail_3rd_vehicle(self):
        if self.x_order_detail_3rd:
            self.x_model_type_id = self.x_order_detail_3rd.model_type_id
            self.x_body_type_id = self.x_order_detail_3rd.body_type_id
      
            
    def _onchange_x_partner_name(self):
        if self.x_partner_name:
            self.x_customer = self.x_partner_name.name
            
    def _onchange_x_partner_id_address(self):
        if self.x_partner_name:
            self.x_address = self.x_partner_name.street or '' 
    
    def _onchange_x_partner_id_province(self):
        if self.x_partner_name:
            self.x_partner_name = self.x_partner_name.state_id.id   
    
    @api.constrains('x_quantity')
    def _check_quantity(self):
        """Kiểm tra số lượng không âm."""
        for record in self:
            if record.x_quantity <= 0:
                raise ValidationError("Số lượng phải lớn hơn 0.")             
            
