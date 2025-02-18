from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CRMFollowUp(models.Model):
    _name = "crm.follow.up"
    _description = "Customer Follow-Up"

    lead_id = fields.Many2one('crm.lead', string='Lead')

    x_day_contact = fields.Date(string="Day", help="Customer follow-up day.")
    x_exchange_content = fields.Text(string="Exchange Content", help="Content of each customer meeting.")
    x_result = fields.Text(string="Result", help="Results after discussion with customers.")
    x_recommendations = fields.Text(string="Recommendations", help="Suggested comments after discussion.")
    x_sale_person_follow_up = fields.Many2one('hr.employee', string="Salesperson Follow-Up",
                                              domain=[('job_title', '=', 'Sales staff')],
                                              help="Salesperson Follow-Up")

    x_sale_person_follow_up_id = fields.Many2one('hr.employee', string="Salesperson Follow-Up ID")

    @api.constrains('x_day_contact')
    def _check_day_contact(self):
        for record in self:
            is_set_in_the_past = record.x_day_contact < fields.Date.today()
            print(f"================================: {is_set_in_the_past}")
            if record.x_day_contact < fields.Date.today():
                raise ValidationError("The day contact cannot be set in the past!")
