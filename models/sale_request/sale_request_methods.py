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

    @api.depends('x_customer_id')
    def _compute_old_customer(self):
        for record in self:
            record.x_old_customer = bool(
                record.x_customer_id and
                self.env['res.partner'].search_count([('id', '=', record.x_customer_id.id)]) > 0
            )

    def action_submit(self):
        for record in self:
            if record.x_customer_type in ["third_party", "box_packer"]:
                if not self.env['sale.region'].check_region(record.x_dealer_id, record.x_city_id):
                    missing_info = any(not line.customer_id for line in record.sale_detail_ids)
                    if missing_info:
                        raise UserError("OUT-OF-AREA SALE: PLEASE COMPLETE THE END CUSTOMER INFORMATION.")

            old_state = record.x_state

            vals = {
                'x_state': 'pending',
                'x_request_date': fields.Date.today()
            }
            record.write(vals)

    def action_approve(self):
        if not self:
            raise ValidationError("No record found for approval.")
        if not self.exists():
            raise ValidationError("The request must be saved before approval.")
        if not self.id:
            raise ValidationError("The request must be saved before approval.")

        employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if not employee:
            raise ValidationError("You must be an employee to approve this request.")

        self.env['sales.request.approval'].create({
            'x_request_id': self.id,
            'x_confirmer_id': employee.id,
            'x_department_id': employee.department_id.id,
            'x_position_id': employee.job_id.id,
            'x_state_from': 'pending',
            'x_state_to': 'approved',
            'x_confirm_date': fields.Date.today(),
            'x_reason': self.x_reason or 'Auto-approved',
        })
        self.x_state = 'approved'

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
