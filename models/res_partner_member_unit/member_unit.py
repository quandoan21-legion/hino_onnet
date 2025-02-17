from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MemberUnit(models.Model):
    _name = 'member.unit'

    lead_id = fields.Many2one('crm.lead', string='Lead')

    # Notebook
    member_id = fields.Many2one('res.partner', string="Member's Name")

    @api.model
    def create(self, vals):
        lead = self.env['crm.lead'].browse(vals.get('lead_id'))
        if lead and lead.x_status != 'draft':
            raise ValidationError(
                "You can't add new Member Unit due to this lead is not in DRAFT status."
            )
        return super(MemberUnit, self).create(vals)
