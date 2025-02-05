from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CRMFollowUp(models.Model):
    _name = "crm.follow.up"
    _description = "Customer Follow-Up"

    lead_id = fields.Many2one('crm.lead', string='Lead')
    x_readonly_fields = fields.Boolean(related='lead_id.x_readonly_fields')
    x_day_contact = fields.Date(string="Day", help="Customer follow-up day.")
    x_sale_person_follow_up = fields.Many2one('hr.employee', string="Salesperson Follow-Up",
                                              domain=[('job_id.name', '=', 'Sales staff')],
                                              help="Salesperson Follow-Up")
    x_sale_person_follow_up_id = fields.Many2one('hr.employee', string="Salesperson Follow-Up ID")

@api.constrains('x_day_contact')
def _check_day_contact(self):
    for record in self:
        if record.x_day_contact > fields.Date.today():
            raise ValidationError("The day contact cannot be set in the future")
