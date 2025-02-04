from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

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
    def _onchange_fields(self):
        if self.x_order_detail_3rd:
            self.x_partner_name = self.x_order_detail_3rd.partner_id
            self.x_customer = self.x_order_detail_3rd.partner_id.name
            self.x_address = self.x_order_detail_3rd.partner_id.street
            self.x_province_id = self.x_order_detail_3rd.partner_id.state_id
            self.x_model_type_id = self.x_order_detail_3rd.model_type_id
            self.x_body_type_id = self.x_order_detail_3rd.body_type_id

        elif self.x_partner_name:
            self.x_customer = self.x_partner_name.name
            self.x_address = self.x_partner_name.street or ''
            self.x_province_id = self.x_partner_name.state_id
            

    @api.constrains('x_customer', 'x_address', 'x_expected_implementation_time', 'x_expected_time_sign_contract')
    def _check_fields(self):
        for record in self:
            if not record.x_customer:
                raise ValidationError("Khách hàng không được để trống.")
            if not re.match("^[a-zA-Z\s]+$", record.x_customer):
                raise ValidationError("Tên khách hàng không được chứa số và ký tự đặc biệt.")
        
            if not record.x_address or record.x_address.isdigit():
                raise ValidationError("Địa chỉ không được chỉ chứa số.")
            if not any(char.isdigit() for char in record.x_address) and not any(char.isalpha() for char in record.x_address):
                raise ValidationError("Địa chỉ phải bao gồm cả chữ và số.")
            
            # if record.x_quantity <= 0:
            #     raise ValidationError("Số lượng phải lớn hơn 0 và là số hợp lệ.")

            if record.x_expected_implementation_time and record.x_expected_time_sign_contract:
                if record.x_expected_implementation_time < record.x_expected_time_sign_contract:
                    raise ValidationError("Ngày giao dự kiến không thể trước ngày ký hợp đồng dự kiến.")  
                  
    @api.constrains('x_quantity')
    def _check_quantity(self):
        for record in self:
            try:
                quantity = float(record.x_quantity)
                if quantity <= 0:
                    raise ValidationError("Số lượng phải lớn hơn 0 và là số hợp lệ.")
            except (ValueError, TypeError):
                raise ValidationError("Số lượng phải là số hợp lệ.")        
