from odoo import models, fields


class CrmLeadContactPerson(models.Model):
    _name = 'crm.lead.contact.person'
    _description = 'Contact'

    lead_id = fields.Many2one('crm.lead', string='Lead')

    x_readonly_fields = fields.Boolean(related='lead_id.x_readonly_fields', store=True)
    x_name = fields.Char(compute="_compute_contact_info", inverse="_inverse_contact_info", string="Contact",
                         help="Other customer contact name!")
    x_email = fields.Char(compute="_compute_contact_info", inverse="_inverse_contact_info", string="Email",
                          help="Customer email address")
    x_function = fields.Char(compute="_compute_contact_info", inverse="_inverse_contact_info", string="Position",
                             help="Customer's position")
    x_phone_number = fields.Char(compute="_compute_contact_info", inverse="_inverse_contact_info",
                                 string="Phone number",
                                 help="Customer's phone number")

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