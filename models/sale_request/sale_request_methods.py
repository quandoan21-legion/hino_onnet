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

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super().get_view(view_id, view_type, **options)
        if view_type == 'tree' and 'arch' in res:
            res['arch'] = res['arch'].replace('<tree>', '<tree create="false">')
        return res

    @api.depends('x_province_id')
    def _compute_customer_region(self):
        for record in self:
            if record.province_id:
                record.customer_region = self.env['sale.area'].search([
                    ('province_ids', 'in', record.province_id.id)
                ], limit=1)

    @api.depends('x_customer_id', 'x_identification_id', 'x_business_registration')
    def _compute_old_customer(self):
        for record in self:
            record.x_old_customer = False
            if record.x_customer_id or self.env['res.partner'].search([
                ('identification_id', '=', record.x_identification_id),
                ('business_registration', '=', record.x_business_registration)
            ], limit=1):
                record.x_old_customer = True

    @api.depends('x_sale_detail_ids.qty_done', 'x_sale_detail_ids.qty_confirmed')
    def _compute_sale_status(self):
        for record in self:
            if record.x_state in ['approved', 'partial_sale', 'completed'] and record.x_sale_detail_ids:
                total_done = sum(record.x_sale_detail_ids.mapped('qty_done'))
                total_confirmed = sum(record.x_sale_detail_ids.mapped('qty_confirmed'))
                if total_done == total_confirmed:
                    record.x_state = 'completed'
                elif total_done > 0:
                    record.x_state = 'partial_sale'

    @api.onchange('x_customer_id')
    def _onchange_customer_id(self):
        if self.x_customer_id:
            self.x_customer_name = self.x_customer_id.name
            self.x_customer_address = self.x_customer_id.street
            self.x_province_id = self.x_customer_id.state_id
            self.x_lead_code_id = self.env['crm.lead'].search([
                ('partner_id', '=', self.x_customer_id.id)
            ], order="create_date desc", limit=1)

    @api.onchange('x_lead_code_id')
    def _onchange_lead_code_id(self):
        if self.x_lead_code_id:
            self.x_customer_name = self.x_lead_code_id.contact_name
            self.x_customer_address = self.x_lead_code_id.street
            self.x_province_id = self.x_lead_code_id.state_id
            self.x_customer_id = False

    @api.onchange('x_customer_type', 'x_province_id')
    def _check_region(self):
        if self.x_customer_type in ['third_party', 'box_packer'] and not self.x_province_id:
            return {'warning': {'title': 'Warning', 'message': 'Province must be set for this customer type'}}

    @api.constrains('x_expected_sale_date')
    def _check_expected_sale_date(self):
        for record in self:
            if record.x_expected_sale_date and record.x_expected_sale_date < fields.Date.today():
                raise ValidationError('Expected sale date cannot be in the past')

    @api.constrains('x_attach_file', 'x_attach_filename')
    def _check_file_type(self):
        for record in self:
            if record.x_attach_file and not record.x_attach_filename.lower().endswith('.pdf'):
                raise ValidationError('Only PDF files are allowed')
            
    def action_submit(self):
        self.ensure_one()
        self._check_region()
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
        for request in self:
            if request.x_state != 'draft':
                raise ValidationError(_('Only draft requests can be canceled.'))
            if self.env.user != request.create_uid:
                raise ValidationError(_('Only the creator can cancel this request.'))
            if not request.x_cancellation_reason:
                raise ValidationError(_('Provide a cancellation reason.'))
            request.write({'x_state': 'cancelled'})
            request.message_post(body=f'Request cancelled. Reason: {request.x_cancellation_reason}')
        return True
