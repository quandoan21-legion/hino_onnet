import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CustomLead(models.Model):
    _inherit = 'crm.lead'

    custom_field = fields.Char(string='Custom Field')
    # x_partner_rank_id = fields.Many2one('res.partner.rank', string='Rank')

    x_partner_id = fields.Many2one('res.partner', string='Customer')
    x_partner_name = fields.Char(string='Customer Name', compute='_compute_customer_name', store=True)
    x_customer_status = fields.Selection(
        [
            ('personal', 'Cá nhân'),
            ('company', 'Công ty'),
            ('internal_hmv', 'Nội bộ HMV')
        ],
        string="Customer Status",
        default='personal'
    )

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
    x_state_id = fields.Many2one(
        'res.country.state', string="State/Province"
    )

    x_website = fields.Char(string="Website")
    x_contact_address_complete = fields.Char(
        string="Địa chỉ cụ thể",
        help="Địa chỉ chi tiết của khách hàng."
    )

    @api.depends('x_partner_id')
    def _compute_customer_name(self):
        for record in self:
            record.x_partner_name = record.x_partner_id.name if record.x_partner_id else ''

    @api.constrains('x_customer_status', 'x_indentity_number', 'x_vat')
    def _check_customer_status_requirements(self):
        for record in self:
            if record.x_customer_status == 'personal' and not record.x_indentity_number:
                raise ValidationError("Với 'Cá nhân', trường 'Số CCCD/CMND' là bắt buộc.")
            if record.x_customer_status == 'company' and not record.x_vat:
                raise ValidationError("Với 'Công ty', trường 'Số ĐKKD (Mã số thuế)' là bắt buộc.")


    @api.constrains('x_indentity_number')
    def _check_identity_number(self):
        for record in self:
            if record.x_indentity_number:
                if not re.match(r'^\d{9,13}$', record.x_indentity_number):
                    raise models.ValidationError("Số CCCD/CMT phải chứa từ 9 đến 13 chữ số.")

