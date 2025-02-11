from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ThirdPartyRegistration(models.Model):
    _name = 'third.party.registration'
    _description = 'Third Party Registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'x_registration_code desc'
    _rec_name = 'x_name'

    # Basic Information
    x_name = fields.Char(string='3rd Unit Register/Packaging House', required=True)
    x_registration_code = fields.Char(string='Registration Code', readonly=True, copy=False, tracking=True)
    x_customer_id = fields.Many2one('res.partner', string='Customer Name', required=True, tracking=True)
    x_customer_code = fields.Char(related='x_customer_id.x_customer_code', string='Customer Code', readonly=True)
    x_representative_id = fields.Many2one('res.partner', string='Representative', required=True, tracking=True)
    x_phone = fields.Char(string='Phone', required=True, tracking=True)
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
    x_note = fields.Text(string='Note', tracking=True)
    x_rejection_reason = fields.Text(string='Rejection Reason', tracking=True)
    x_attach_files = fields.Many2many(
        'ir.attachment',
        'third_party_attach_rel',
        'third_party_id',
        'attachment_id',
        string='Attach Files'
    )
    x_approval_ids = fields.One2many('third.party.registration.approval', 'registration_id', string='Approvals')

    @api.model
    def create(self, vals):
        if not vals.get('x_registration_code'):
            vals['x_registration_code'] = self.env['ir.sequence'].next_by_code('third.party.registration.sequence')
        return super().create(vals)

    def action_submit(self):
        """Submit registration for approval"""
        self.ensure_one()
        if self.x_state in ['draft', 'rejected']:
            self.write({'x_state': 'pending'})

    def action_approve(self):
        """Approve registration"""
        self.ensure_one()
        if self.x_state == 'pending':
            self.write({'x_state': 'approved'})
            if self.x_customer_id:
                self.x_customer_id.write({
                    'x_customer_type': self.x_registration_type,
                    'x_register_sale_3rd_id': self.x_registration_code
                })

    def action_reject(self):
        """Reject registration"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reject Registration',
            'res_model': 'third.party.registration.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_x_registration_id': self.id}
        }

    def action_cancel(self):
        """Cancel registration"""
        self.ensure_one()
        if self.x_state == 'draft':
            self.write({'x_state': 'cancelled'})

    def action_create_customer(self):
        """Create customer from approved registration"""
        self.ensure_one()
        if self.x_state != 'approved':
            raise ValidationError('Can only create customer from approved registrations.')

        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Customer',
            'res_model': 'res.partner',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_name': self.x_customer_id.name,
                'default_phone': self.x_phone,
                'default_x_customer_type': self.x_registration_type,
                'default_x_register_sale_3rd_id': self.x_registration_code,
                'default_x_industry_id': self.x_business_field_id.id,
            }
        }

    @api.constrains('x_phone')
    def _check_phone_number(self):
        """Validate phone number format"""
        for record in self:
            if record.x_phone:
                if not record.x_phone.startswith('0') or not record.x_phone[1:].isdigit() or len(record.x_phone) > 11:
                    raise ValidationError("Phone number must start with 0 and contain no more than 10 digits.")