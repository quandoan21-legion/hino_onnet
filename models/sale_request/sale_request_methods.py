from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from datetime import timedelta, date

class SaleRequestMethods(models.Model):
    _inherit = 'sale.request'

    @api.model
    def create(self, vals):
        if not vals.get('x_request_code'):
            vals['x_request_code'] = self.env['ir.sequence'].next_by_code('sale.request.sequence')
        return super(SaleRequestMethods, self).create(vals)

    def _generate_request_code(self):
        return self.env['ir.sequence'].next_by_code('sale.request.sequence') or '/'

    @api.onchange('x_dealer_branch_id')
    def _onchange_dealer_branch_id(self):
        if self.x_dealer_branch_id and self.x_dealer_branch_id.parent_id:
            self.x_request_dealer_id = self.x_dealer_branch_id.parent_id
        else:
            self.x_request_dealer_id = False

    @api.depends('x_province_id')
    def _compute_customer_region(self):
        for record in self:
            if record.x_province_id:
                sale_area_detail = self.env['sales.area.detail.line'].search([('x_code', '=', record.x_province_id.id)],
                                                                             limit=1)
                record.x_customer_region = sale_area_detail.x_sale_area_id if sale_area_detail else False
            else:
                record.x_customer_region = False

    @api.depends('x_dealer_branch_id')
    def _compute_request_dealer_id(self):
        for record in self:
            record.x_request_dealer_id = record.x_dealer_branch_id.parent_id if record.x_dealer_branch_id else False

    @api.onchange('x_customer_id')
    def _onchange_x_customer_id(self):
        if self.x_customer_id:
            self.x_customer_name = self.x_customer_id.name
            self.x_customer_address = self.x_customer_id.street

    @api.depends('x_customer_id')
    def _compute_old_customer(self):
        for record in self:
            record.x_old_customer = bool(
                record.x_customer_id and
                self.env['res.partner'].search_count([('id', '=', record.x_customer_id.id)]) > 0
            )

    @api.depends('x_lead_code_id')
    def _compute_readonly_customer(self):
        for record in self:
            record.x_customer_id.readonly = bool(record.x_lead_code_id)

    def check_region(self, dealer_id, city_id):
        return bool(self.env['sale.area'].search([
            ('dealer_id', '=', dealer_id),
            ('city_id', '=', city_id),
        ], limit=1))

    @api.constrains('x_expected_sale_date', 'x_expected_to_sign_contract')
    def _check_expected_dates(self):
        for record in self:
            today = date.today()

            if record.x_expected_sale_date and record.x_expected_sale_date < today:
                raise ValidationError("Expected Sale Date must be greater than or equal to the current date.")

            if record.x_expected_to_sign_contract and record.x_expected_to_sign_contract < today:
                raise ValidationError(
                    "Expected to Sign Contract Date must be greater than or equal to the current date.")

            if (record.x_expected_sale_date and record.x_expected_to_sign_contract and
                    record.x_expected_to_sign_contract < record.x_expected_sale_date):
                raise ValidationError(
                    "Expected to Sign Contract Date must be greater than or equal to the Expected Sale Date.")

    def action_submit(self):
        for record in self:
            if record.x_state != 'draft':
                raise UserError(_("The request form is not in Draft state!"))

            sale_region = self.env['sale.region'].search([
                ('x_dealer_branch_id', '=', record.x_dealer_branch_id.id)
            ], limit=1)

            if not sale_region:
                raise UserError(_("No sales region found for the dealer"))

            allowed_areas = sale_region.x_field_sale_ids.ids

            if record.x_customer_type in ['third_party', 'builder']:
                if record.x_province_id.id not in allowed_areas:
                    missing_customers = record.sale_detail_ids.filtered(lambda d: not d.x_customers_use_id)

                    if missing_customers:
                        raise UserError(_("OUT-OF-REGION SALE, PLEASE PROVIDE COMPLETE END CUSTOMER INFORMATION."))

            record.x_state = 'pending'

    def action_approve(self):
        self.ensure_one()

        if not self:
            raise ValidationError("No record found for approval.")
        if not self.exists():
            raise ValidationError("The request must be saved before approval.")
        if not self.id:
            raise ValidationError("The request must be saved before approval.")

        employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if not employee:
            raise ValidationError("You must be an employee to approve this request.")

        if self.x_customer_id:
            allowed_dealers = self.x_customer_id.x_allow_dealer_id

            if self.x_request_dealer_id and self.x_request_dealer_id not in allowed_dealers:
                self.x_customer_id.write({
                    'x_allow_dealer_id': [(4, self.x_request_dealer_id.id)]
                })

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
        self.x_approve_date = fields.Date.today()

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
