from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CrmLeadContactPerson(models.Model):
    _name = 'crm.lead.contact.person'
    _description = 'Contact'

    lead_id = fields.Many2one('crm.lead', string='Lead')

    partner_id = fields.Many2one('res.partner', string="Partner")

    x_name = fields.Char(compute="_compute_contact_info", string="Contact",
                         help="Other customer contact name!")
    x_email = fields.Char(compute="_compute_contact_info", string="Email",
                          help="Customer email address")
    x_function = fields.Char(compute="_compute_contact_info", string="Position",
                             help="Customer's position")
    x_phone_number = fields.Char(compute="_compute_contact_info",
                                 string="Phone number",
                                 help="Customer's phone number")

    # def _compute_contact_info(self):
    #     for record in self:
    #         if record.partner_id:
    #             record.x_name = record.partner_id.id.name
    #             record.x_email = record.partner_id.email
    #             record.x_function = record.partner_id.function
    #             record.x_phone_number = record.partner_id.phone

    #
    # @api.model
    # def create(self, vals_list):
    #     for val in vals_list:
    #         lead = self.env["crm.lead"].browse(vals_list.get("lead_id"))
    #         if lead and lead.x_status != 'draft':
    #             ValidationError("You can't create a new Contact due to this lead status is not DRAFT"
    #                             )
    #         super(CrmLeadContactPerson, self).create(vals_list)
