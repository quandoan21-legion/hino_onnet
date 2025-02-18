from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta
class SaleRequestMethods(models.Model):
    _inherit = 'sale.request'

    @api.model
    def create(self, vals):
        if not vals.get('x_request_code'):
            vals['x_request_code'] = self.env['ir.sequence'].next_by_code('sale.request.sequence')
        return super(SaleRequestMethods, self).create(vals)

    def _generate_request_code(self):
        return self.env['ir.sequence'].next_by_code('sale.request.sequence') or '/'

    @api.depends('x_province_id')
    def _compute_customer_region(self):
        for record in self:
            if record.province_id:
                record.customer_region = self.env['sale.area'].search([
                    ('province_ids', 'in', record.province_id.id)
                ], limit=1)
            
    def action_submit(self):
        vals = {'x_state': 'pending', 'x_request_date': fields.Date.today()}
        tracking_values = []
        for field, value in vals.items():
            old_value = self[field]
            if old_value != value:
                field_record = self.env['ir.model.fields'].search([
                    ('model', '=', self._name),
                    ('name', '=', field)
                ], limit=1)
                if field_record:
                    tracking_values.append((0, 0, {
                        'field_id': field_record.id,
                        'old_value_char': str(old_value) if isinstance(old_value, (str, bool, int, float)) else None,
                        'new_value_char': str(value) if isinstance(value, (str, bool, int, float)) else None,
                    }))
        self.write(vals)
        
        self.env['mail.activity'].create({
            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            'note': f'Please review request {self.x_request_code} submitted by {self.env.user.name}',
            'res_id': self.id,
            'res_model_id': self.env['ir.model'].search([('model', '=', self._name)], limit=1).id,
            'summary': f'Review Request {self.x_request_code}',
            # 'user_id': self.x_hmv_approver_id.id,
            'date_deadline': fields.Date.today() + timedelta(days=2)  # Set 2-day deadline
        })

        msg = f"""
            Request submitted for approval
            Submitted by: {self.env.user.name}
            Status: Draft -> Pending
            Date: {fields.Date.today()}
        """
        self.message_post(body=msg, tracking_value_ids=tracking_values)

    def action_approve(self):
        self.ensure_one()
        vals = {'x_state': 'approved', 'x_approve_date': fields.Date.today()}
        self.write(vals)
        msg = f"""
            Request approved
            Approved by: {self.env.user.name}
            Status: Pending -> Approved
            Date: {fields.Date.today()}
        """
        self.message_post(body=msg)

    def action_refuse(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Enter Refusal Reason',
            'res_model': 'sale.request.refuse.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_sale_request_id': self.id}
        }

    def action_cancel(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Enter Cancel Reason',
            'res_model': 'sale.request.cancel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_sale_request_id': self.id}
        }
