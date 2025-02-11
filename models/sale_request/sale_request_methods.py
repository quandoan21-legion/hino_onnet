from odoo import models, fields,api
from odoo.exceptions import ValidationError
from datetime import datetime

class SaleRequestMethods(models.Model):
    _inherit = 'sale.request'

    # Override Methods
    @api.model
    def create(self, vals):
        if not vals.get('x_request_code'):
            vals['x_request_code'] = self.env['ir.sequence'].next_by_code('sale.request.sequence')
        return super(SaleRequestMethods, self).create(vals)

    def _generate_request_code(self):
        sequence = self.env['ir.sequence'].next_by_code('sale.request.sequence') or '/'
        return sequence
    
    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super().get_view(view_id, view_type, **options)
        if view_type == 'tree':
            if 'arch' in res:
                res['arch'] = res['arch'].replace('<tree>', '<tree create="false">')
        return res

    # Compute Methods
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
            if record.x_customer_id:
                record.x_old_customer = True
            elif record.x_identification_id:
                existing = self.env['res.partner'].search([
                    ('identification_id', '=', record.x_identification_id)
                ], limit=1)
                record.x_old_customer = bool(existing)
            elif record.x_business_registration:
                existing = self.env['res.partner'].search([
                    ('business_registration', '=', record.x_business_registration)
                ], limit=1)
                record.x_old_customer = bool(existing)

    # Validation Methods
    @api.constrains('x_expected_sale_date')
    def _check_expected_sale_date(self):
        for record in self:
            if record.x_expected_sale_date and record.x_expected_sale_date < fields.Date.today():
                raise ValidationError('Ngày dự kiến bán không được nhỏ hơn ngày hiện tại')

    @api.constrains('x_attach_file')
    def _check_file_type(self):
        for record in self:
            if record.x_attach_file and not record.x_attach_filename.lower().endswith('.pdf'):
                raise ValidationError('Chỉ cho phép đính kèm file PDF')

    # Action Methods
    def action_submit(self):
        self.ensure_one()
        self.write({
            'x_state': 'pending',
            'x_request_date': fields.Date.today()
        })

    def action_approve(self):
        self.ensure_one()
        self.write({
            'x_state': 'approved',
            'x_approve_date': fields.Date.today()
        })

    def action_refuse(self):
        self.ensure_one()
        self.write({
            'x_state': 'rejected',
            'x_approve_date': fields.Date.today()
        })

    def action_cancel(self):
        self.ensure_one()
        self.write({
            'x_state': 'cancelled',
            'x_approve_date': fields.Date.today()
        })

    def action_partial_sale(self):
        self.ensure_one()
        if self.x_state != 'approved':
            raise ValidationError("Can only transition to 'Partial Sale' after approval.")

        self.write({
            'x_state': 'partial_sale'
        })

    def action_complete(self):
        self.ensure_one()
        if self.x_state not in ['approved', 'partial_sale']:
            raise ValidationError("Can only mark as 'Completed' if in 'Approved' or 'Partial Sale' state.")

        self.write({
            'x_state': 'completed'
        })
        
    def action_send_mail(self):
        self.ensure_one()
        template = self.env.ref('your_module.sale_request_mail_template', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)