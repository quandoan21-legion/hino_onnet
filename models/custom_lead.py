
import re

from odoo import models, fields, api


class CustomLead(models.Model):
    _inherit = 'crm.lead'

    custom_field = fields.Char(string='Custom Field')
    # x_partner_rank_id = fields.Many2one('res.partner.rank', string='Rank')

    x_customer_id = fields.Many2one('res.partner', string='Customer')
    x_customer_name = fields.Char(string='Customer Name', compute='_compute_customer_name', store=True)

    # x_customer_id = fields.Many2one('res.partner', string='Customer')
    # x_customer_real_id = fields.Char(string='Customer ID', compute='_compute_customer_real_id', store=True, readonly=True)
    # x_customer_name = fields.Char(string='Customer Name')

    x_customer_type = fields.Selection(
        [('nhap', 'Nháp'), ('don_vi_thu_3', 'Đơn vị thứ 3'), ('nha_dong_thung', 'Nhà đóng thùng')],
        string='Bên thứ 3/Nhà đóng thùng ', default='nhap'
    )
    x_phone = fields.Char(string='Số điện thoại')
    x_email_from = fields.Char(string='Email')
    x_vat = fields.Char(string='Số ĐKKD (Mã số thuế)')
    x_indentity_number = fields.Char(string='CCCD/CMT')
    x_industry_id = fields.Many2one('res.partner.industry', string='Lĩnh vực kinh doanh')
    # x_request_sale_3rd_barrels_id = fields.Many2one('res.request.sale.3rd.barrels', string='Đề nghị bán lấn vùng/Bên thứ 3/Nhà đóng thùng', readonly=True)
    x_purchase_type = fields.Selection(
        [('mua_sam_truc_tiep', 'Mua sắm trực tiếp'), ('dau_thau', 'Đấu thầu'), ('khac', 'Khác')],
        string='Loại hình mua hàng'
    )
    x_service_contract = fields.Boolean(string='Hợp đồng dịch vụ')
    x_activity_area = fields.Char(string='Phạm vi hoạt động')
    x_dealer_id = fields.Many2one('res.partner', string='Đại lý')
    x_dealer_branch_id = fields.Many2one('res.partner', string='Chi nhánh đại lý')
    x_sale_person_id = fields.Many2one('res.users', string='Nhân viên kinh doanh')
    x_approaching_channel_id = fields.Many2one('hr.employee', string='Kênh tiếp cận')


    @api.depends('x_customer_id')
    def _compute_customer_name(self):
        for record in self:
            record.x_customer_name = record.x_customer_id.name if record.x_customer_id else ''

    # @api.depends('x_customer_id')
    # def _compute_customer_real_id(self):
    #     for record in self:
    #         record.x_customer_real_id = str(record.x_customer_id.id) if record.x_customer_id else ''
    #         record.x_customer_name = record.x_customer_id.name if record.x_customer_id else ''


    # @api.onchange('partner_id')
    # def _onchange_partner_id(self):
    #     if self.partner_id:
    #         self.x_indentity_number = self.partner_id.identity_number
    #         self.x_vat = self.partner_id.vat_number


    @api.constrains('x_indentity_number')
    def _check_identity_number(self):
        for record in self:
            if record.x_indentity_number:
                if not re.match(r'^\d{9,13}$', record.x_indentity_number):
                    raise models.ValidationError("Số CCCD/CMT phải chứa từ 9 đến 13 chữ số.")

