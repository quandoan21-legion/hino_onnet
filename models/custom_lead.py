from odoo import models, fields

class CustomLead(models.Model):
    _inherit = 'crm.lead'

    custom_field = fields.Char(string='Custom Field')
    # x_partner_rank_id = fields.Many2one('res.partner.rank', string='Rank')
    x_customer_type = fields.Selection(
        [('nhap', 'Nháp'), ('don_vi_thu_3', 'Đơn vị thứ 3'), ('nha_dong_thung', 'Nhà đóng thùng')], 
        string='Bên thứ 3/Nhà đóng thùng ', default='nhap'
    )    
    x_phone = fields.Char(string='Số điện thoại')
    x_email_from = fields.Char(string='Email')
    x_vat = fields.Many2one('res.partner', string='Số ĐKKD (Mã số thuế)') 
    x_indentity_number = fields.Many2one('res.partner', string='CCCD/CMT')
    x_industry_id = fields.Many2one('res.partner.industry', string='Lĩnh vực kinh doanh')