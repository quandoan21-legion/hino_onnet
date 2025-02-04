
import re

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CustomLead(models.Model):
    _inherit = 'crm.lead'
    # Notebook lines
    x_member_line_ids = fields.One2many('member.line', 'lead_id', string='Member Lines')
    x_owned_team_car_line_ids = fields.One2many('owned.team.car.line', 'lead_id', string='Owned Team Car Lines')

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
    x_partner_id = fields.Many2one('res.partner', string='Customer', tracking=True)
    x_partner_name = fields.Char(string='Customer Name', compute='_compute_customer_name', store=True, tracking=True)

    # x_customer_id = fields.Many2one('res.partner', string='Customer')
    # x_customer_real_id = fields.Char(string='Customer ID', compute='_compute_customer_real_id', store=True, readonly=True)
    # x_customer_name = fields.Char(string='Customer Name')

    x_customer_type = fields.Selection(
        [('nhap', 'Nháp'), ('don_vi_thu_3', 'Đơn vị thứ 3'), ('nha_dong_thung', 'Nhà đóng thùng')],
        string='Bên thứ 3/Nhà đóng thùng ', default='nhap', tracking=True
    )
    x_phone = fields.Char(string='Số điện thoại', tracking=True)
    x_email_from = fields.Char(string='Email', tracking=True)
    x_vat = fields.Char(string='Số ĐKKD (Mã số thuế)', tracking=True)
    x_identity_number = fields.Char(string='CCCD/CMT', tracking=True)
    x_industry_id = fields.Many2one('res.partner.industry', string='Lĩnh vực kinh doanh', tracking=True)
    # x_request_sale_3rd_barrels_id = fields.Many2one('res.request.sale.3rd.barrels', string='Đề nghị bán lấn vùng/Bên thứ 3/Nhà đóng thùng', readonly=True)
    x_purchase_type = fields.Selection(
        [('mua_sam_truc_tiep', 'Mua sắm trực tiếp'), ('dau_thau', 'Đấu thầu'), ('khac', 'Khác')],
        string='Loại hình mua hàng', tracking=True
    )
    x_bidding_package = fields.Char(string='Gói thầu', tracking=True)
    x_project = fields.Char(string='Dự án', tracking=True)
    x_estimated_time_of_bid_opening = fields.Date(string='Thời gian dự kiến mở thầu', tracking=True)
    x_area = fields.Char(string='Khu vực', tracking=True)
    x_service_contract = fields.Boolean(string='Hợp đồng dịch vụ', tracking=True)
    x_activity_area = fields.Char(string='Phạm vi hoạt động', tracking=True)
    x_dealer_id = fields.Many2one('res.partner', string='Đại lý', readonly=True)
    x_dealer_branch_id = fields.Many2one('res.company', string='Chi nhánh đại lý', default=lambda self: self.env.company, help='Chi nhánh đại lý tạo Tiềm năng', tracking=True)
    x_sale_person_id = fields.Many2one('hr.employee', string='Nhân viên kinh doanh', domain=[('job_id.name', '=', 'Nhân viên kinh doanh')], help='Nhân viên kinh doanh phụ trách tiềm năng', tracking=True)
    x_approaching_channel_id = fields.Many2one('hr.employee', string='Kênh tiếp cận', tracking=True)
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

    @api.onchange('x_partner_id')
    def _onchange_x_partner_id(self):
        if self.x_partner_id:
            self.x_phone = self.x_partner_id.phone
            self.x_email_from = self.x_partner_id.email
            self.x_vat = self.x_partner_id.vat
            self.x_identity_number = self.x_partner_id.identity_number
            self.x_industry_id = self.x_partner_id.industry_id
            self.x_service_contract = self.x_partner_id.service_contract if hasattr(self.x_partner_id, 'service_contract') else False
            self.x_activity_area = self.x_partner_id.activity_area if hasattr(self.x_partner_id, 'activity_area') else ''

    # @api.depends('x_customer_id')
    # def _compute_customer_real_id(self):
    #     for record in self:
    #         record.x_customer_real_id = str(record.x_customer_id.id) if record.x_customer_id else ''
    #         record.x_customer_name = record.x_customer_id.name if record.x_customer_id else ''


    x_vehicle_interest_ids = fields.One2many(
        'crm.lead.vehicle.interest.line',
        'lead_id',
        string='Loại xe khách hàng quan tâm'
    )

    x_contact_person_ids = fields.One2many('crm.lead.contact.person', 'lead_id', string='Contact')

    @api.depends('x_partner_id')
    def _compute_customer_name(self):
        for record in self:
            record.x_partner_name = record.x_partner_id.name if record.x_partner_id else ''

    # @api.onchange('partner_id')
    # def _onchange_partner_id(self):
    #     if self.partner_id:
    #         self.x_identity_number = self.partner_id.identity_number
    #         self.x_vat = self.partner_id.vat_number:
    @api.constrains('x_customer_status', 'x_identity_number', 'x_vat')
    def _check_customer_status_requirements(self):
        for record in self:
            if record.x_customer_status == 'personal' and not record.x_identity_number:
                raise ValidationError("Với 'Cá nhân', trường 'Số CCCD/CMND' là bắt buộc.")
            if record.x_customer_status == 'company' and not record.x_vat:
                raise ValidationError("Với 'Công ty', trường 'Số ĐKKD (Mã số thuế)' là bắt buộc.")


    @api.constrains('x_identity_number')
    def _check_identity_number(self):
        for record in self:
            if record.x_identity_number:
                if not re.match(r'^\d{9,13}$', record.x_identity_number):
                    raise models.ValidationError("Số CCCD/CMT phải chứa từ 9 đến 13 chữ số.")

    @api.onchange('state')
    def _onchange_state(self):
        if self.state != 'draft':
            self.salesperson_id = False