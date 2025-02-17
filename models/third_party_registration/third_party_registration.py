from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

# Initialize logger
_logger = logging.getLogger(__name__)

# Import translation function
from odoo.tools.translate import _

class ThirdPartyRegistration(models.Model):
    _name = 'third.party.registration'
    _description = 'Third Party Registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'x_registration_code desc'
    _rec_name = 'x_registration_code'

    # Basic Information
    x_name = fields.Char(string='3rd Unit Register/Packaging House', required=True)
    x_registration_code = fields.Char(string='Registration Code', readonly=True, copy=False, tracking=True)
    x_customer_id = fields.Many2one('res.partner', string='Customer Name', required=True, tracking=True)
    x_customer_code = fields.Char(related='x_customer_id.x_customer_code', string='Customer Code', readonly=True)
    x_representative_id = fields.Many2one('res.partner', string='Representative', required=True, tracking=True)
    x_phone = fields.Char(
        related='x_customer_id.phone',  # Relate to customer's phone
        string='Phone',
        store=True,  # Store the value for performance
        readonly=False,  # Allow editing
        tracking=True
    )
    x_business_field_id = fields.Many2one('res.partner.industry', string='Business Field', tracking=True)
    x_registration_type = fields.Selection([
        ('last_customer', 'Last Customer'),
        ('third_party', 'Third Party'),
        ('body_maker', 'Body Maker')
    ], string='Registration Type', required=True, default='third_party', tracking=True)

    # Status Management
    x_state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    # Additional Information
    x_attach_files = fields.Binary(string='Attach Files', attachment=True)
    x_ability_distribute_standards = fields.Boolean(
        string='Ability to distribute cartons according to HMV standards',
        default=False,
        tracking=True
    )
    x_barrels_3rd_processes = fields.Boolean(
        string='3rd processes barrels',
        default=False,
        tracking=True
    )
    x_unit_3rd_commercial = fields.Boolean(
        string='3rd commercial unit',
        default=False,
        tracking=True
    )
    x_note = fields.Text(string='Reason for selling', tracking=True)
    x_rejection_reason = fields.Text(string='Rejection Reason', tracking=True)
    x_attach_files = fields.Many2many(
        'ir.attachment',
        'third_party_attach_rel',
        'third_party_id',
        'attachment_id',
        string='Attach Files'
    )
    x_approval_ids = fields.One2many('third.party.registration.approval', 'registration_id', string='Approvals')

    @api.constrains('x_attach_files')
    def _check_attachment_type(self):
        for record in self:
            for attachment in record.x_attach_files:
                if attachment.mimetype and not attachment.mimetype.startswith('application/pdf'):
                    raise ValidationError(_('Only PDF files are allowed! File "%s" is not a PDF.') % attachment.name)

    @api.model
    def create(self, vals):
        if not vals.get('x_registration_code'):
            vals['x_registration_code'] = self.env['ir.sequence'].next_by_code('third.party.registration.sequence')
        return super().create(vals)

    @api.onchange('x_customer_id')
    def _onchange_customer_id(self):
        if self.x_customer_id and self.x_customer_id.phone:
            self.x_phone = self.x_customer_id.phone

    def action_submit(self):
        """Submit registration for approval"""
        self.ensure_one()
        if self.x_state in ['draft', 'rejected']:
            # Create approval log before state change
            self.env['third.party.registration.approval'].create({
                'registration_id': self.id,
                'x_approval_person': self.env.user.id,
                'x_department': self.env.user.employee_id.department_id.id if self.env.user.employee_id else False,
                'x_position': self.env.user.employee_id.job_id.id if self.env.user.employee_id else False,
                'x_previous_state': self.x_state,
                'x_new_state': 'pending',
            })
            self.write({'x_state': 'pending'})

    def action_approve(self):
        """Approve registration"""
        self.ensure_one()
        if self.x_state == 'pending':
            # Create approval log before state change
            self.env['third.party.registration.approval'].create({
                'registration_id': self.id,
                'x_approval_person': self.env.user.id,
                'x_department': self.env.user.employee_id.department_id.id if self.env.user.employee_id else False,
                'x_position': self.env.user.employee_id.job_id.id if self.env.user.employee_id else False,
                'x_previous_state': 'pending',
                'x_new_state': 'approved',
            })
            self.write({'x_state': 'approved'})
            if self.x_customer_id:
                self.x_customer_id.write({
                    'x_customer_type': self.x_registration_type,
                    'x_register_sale_3rd_id': self.id
                })

    def action_reject(self):
        """Reject registration"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reject Registration',
            'res_model': 'third.party.registration.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_registration_id': self.id}
        }

    def action_cancel(self):
        """Cancel registration"""
        self.ensure_one()
        if self.x_state == 'draft':
            # Create approval log before state change
            self.env['third.party.registration.approval'].create({
                'registration_id': self.id,
                'x_approval_person': self.env.user.id,
                'x_department': self.env.user.employee_id.department_id.id if self.env.user.employee_id else False,
                'x_position': self.env.user.employee_id.job_id.id if self.env.user.employee_id else False,
                'x_previous_state': 'draft',
                'x_new_state': 'cancelled',
            })
            self.write({'x_state': 'cancelled'})

    def action_create_customer(self):
        """Update existing customer from approved registration"""
        self.ensure_one()
        if self.x_state != 'approved':
            raise ValidationError('Can only create customer from approved registrations.')

        form_view_id = self.env.ref('hino_onnet.view_form_custom_customer').id
        customer = self.x_customer_id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Update Customer',  # Changed name to reflect what we're doing
            'res_model': 'res.partner',
            'view_mode': 'form',
            'res_id': customer.id,  # Specify the existing record ID
            'views': [
                (form_view_id, 'form'),
            ],
            'target': 'current',
            'context': {
                'default_name': customer.name,
                'default_phone': self.x_phone,
                'default_x_customer_type': self.x_registration_type,
                'default_x_register_sale_3rd_id': self.id,
                'default_x_industry_id': self.x_business_field_id.id,
                'default_x_identity_number': customer.x_identity_number,
                'default_x_customer_code': self.x_customer_code,
            }
        }

    @api.constrains('x_phone')
    def _check_phone_duplicate_and_format(self):
        """
        Server-side validation for phone numbers and duplicates.
        This ensures data integrity even when bypassing the UI.
        """
        for record in self:
            if not record.x_phone:
                continue

            normalized_phone = record.x_phone

            # 1. Basic phone number validation
            if not normalized_phone.startswith('0'):
                raise ValidationError("Phone number must start with 0")

            if len(normalized_phone) != 10:
                raise ValidationError("Phone number must be exactly 10 digits")

            # 2. Check duplicate in res.partner
            partner_domain = [('phone', '=', normalized_phone)]
            if record.x_customer_id:
                partner_domain.append(('id', '!=', record.x_customer_id.id))

            existing_partner = record.env['res.partner'].search(partner_domain, limit=1)
            if existing_partner:
                raise ValidationError(f'Phone number already exists for customer: {existing_partner.name}')

            # 3. Check duplicate in current model
            registration_domain = [
                ('x_phone', '=', normalized_phone),
                ('id', '!=', record.id)
            ]
            existing_registration = record.env['third.party.registration'].search(registration_domain, limit=1)
            if existing_registration:
                raise ValidationError(
                    f'Phone number already exists in registration: {existing_registration.x_name}'
                )