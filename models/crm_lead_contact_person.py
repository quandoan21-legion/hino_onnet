from odoo import models, fields, api

class CrmLeadContactPerson(models.Model):
    _name = 'crm.lead.contact.person'
    _description = 'Liên hệ'

    lead_id = fields.Many2one('crm.lead', string='Lead')

    x_name = fields.Char(compute="_compute_contact_info", inverse="_inverse_contact_info", string="Tên liên hệ",
                         help="Tên liên hệ khác của khách hàng")
    x_email = fields.Char(compute="_compute_contact_info", inverse="_inverse_contact_info", string="Email",
                          help="Địa chỉ email của khách hàng")
    x_function = fields.Char(compute="_compute_contact_info", inverse="_inverse_contact_info", string="Chức vụ",
                             help="Tên chức vụ của khách hàng")
    x_phone_number = fields.Char(compute="_compute_contact_info", inverse="_inverse_contact_info",
                                 string="Số điện thoại",
                                 help="Số điện thoại của khách hàng")

    def _compute_contact_info(self):
        for record in self:
            if record.partner_id:
                record.x_name = record.partner_id.name
                record.x_email = record.partner_id.email
                record.x_function = record.partner_id.function
                record.x_phone_number = record.partner_id.phone

    def _inverse_contact_info(self):
        for record in self:
            if record.partner_id:
                record.partner_id.name = record.x_name
                record.partner_id.email = record.x_email
                record.partner_id.function = record.x_function
                record.partner_id.phone = record.x_phone_number