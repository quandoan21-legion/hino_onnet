from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import re
import logging

# Initialize logger
_logger = logging.getLogger(__name__)

# Import translation function
from odoo.tools.translate import _


class ThirdPartyRegistration(models.Model):
    _name = 'third.party.registration'
    _description = 'Third Party/Packaging House Registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'x_name'

    x_name = fields.Char(string='3rd Unit Register/Packaging House', required=True)
    x_registration_code = fields.Char(string='Registration Code', readonly=True)
    x_customer_name = fields.Many2one('res.partner', string='Customer Name', required=True)
    x_customer_code = fields.Char(related='x_customer_name.ref', string='Customer Code', readonly=True)
    x_representative = fields.Many2one('res.partner', string='Representative', required=True)
    x_phone = fields.Char(related='x_customer_name.phone', string='Phone', required=True)
    x_business_field = fields.Many2one('res.partner.industry', string='Business Field')
    x_registration_type = fields.Selection([
        ('third_party', 'Third Party'),
        ('packaging', 'Packaging Unit'),
        ('body_maker', 'Body Maker')
    ], string='Registration Type', required=True)
    x_attach_files = fields.Many2many(
        'ir.attachment',
        'third_party_reg_attachment_rel',
        'registration_id',
        'attachment_id',
        string='Attachments'
    )
    x_ability_distribute_standards = fields.Boolean(
        string='Able to issue carton paper according to HMV standards',
        default=False  # Explicitly set default
    )
    x_barrels_3rd_processes = fields.Boolean(string='The third unit processes barrels')
    x_unit_3rd_commercial = fields.Boolean(string='Commercial third unit')
    x_note = fields.Text(string='Reason for selling car/Rejection')

    # One2many relation for multiple approvals
    x_approval_ids = fields.One2many('third.party.registration.approval', 'registration_id', string='Approvals')

    x_state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], default='draft', string='State', tracking=True)

    # Add onchange handler for better UX
    def _validate_phone_number(self, phone):
        """
        Validate số điện thoại Việt Nam:
        - Bắt đầu bằng 0 hoặc +84
        - Đầu số: 03, 05, 07, 08, 09 (di động) hoặc 02 (cố định)
        - Tổng độ dài: 10 số nếu bắt đầu bằng 0, 11-12 số nếu bắt đầu bằng +84
        """
        # Loại bỏ khoảng trắng và dấu gạch ngang nếu có
        phone = re.sub(r'[\s-]', '', phone)

        # Pattern cho số bắt đầu bằng 0
        pattern_0 = r'^0(2|3|5|7|8|9)[0-9]{8}$'

        # Pattern cho số bắt đầu bằng +84
        pattern_84 = r'^\+84(2|3|5|7|8|9)[0-9]{8}$'

        if re.match(pattern_0, phone) or re.match(pattern_84, phone):
            return True

        return False

    @api.onchange('x_phone')
    def _onchange_phone(self):
        if self.x_phone and isinstance(self.x_phone, str):
            phone = self.x_phone.strip()
            if not self._validate_phone_number(phone):
                raise ValidationError("""
                    Number is invalid!
                """)

            # Chuẩn hóa số điện thoại về định dạng 0...
            if phone.startswith('+84'):
                phone = '0' + phone[3:]

            # Tìm partner với số điện thoại này or create new
            partner = self.env['res.partner'].search([('phone', '=', phone)], limit=1)
            if not partner:
                partner = self.env['res.partner'].create({
                    'name': f'New Contact ({phone})',
                    'phone': phone,
                })
            self.x_phone = partner.id

    # Add file validation
    @api.constrains('x_attach_files')
    def _check_attachment_type(self):
        for record in self:
            for attachment in record.x_attach_files:
                if not attachment.mimetype == 'application/pdf':
                    raise ValidationError(_('Only PDF files are allowed! File "%s" is not a PDF.') % attachment.name)

    @api.model
    def create(self, vals):
        if not vals.get('x_registration_code'):
            vals['x_registration_code'] = self.env['ir.sequence'].next_by_code('third.party.registration.sequence')
        return super(ThirdPartyRegistration, self).create(vals)

    def action_submit(self):
        self.ensure_one()
        self.write({'x_state': 'waiting_approval'})
        # Create approval log
        self.env['third.party.registration.approval'].create({
            'registration_id': self.id,
            'x_approval_person': self.env.user.id,
            'x_previous_state': 'draft',
            'x_new_state': 'waiting_approval',
        })

    def action_confirm(self):
        self.write({'x_state': 'approved'})

    def action_refuse(self):
        self.ensure_one()
        return {
            'name': _('Reject Registration'),
            'type': 'ir.actions.act_window',
            'res_model': 'third.party.registration.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_registration_id': self.id,
            }
        }

    def action_cancel(self):
        self.write({'x_state': 'cancelled'})

    def action_create_customer(self):
        try:
            category_ids = []
            # Map selection value to category
            category_mapping = {
                'third_party': self.env.ref('your_module.category_third_party').id,
                'packaging': self.env.ref('your_module.category_packaging').id,
                'body_maker': self.env.ref('your_module.category_body_maker').id,
            }

            if self.x_registration_type and self.x_registration_type in category_mapping:
                category_ids = [(4, category_mapping[self.x_registration_type])]

            new_customer = self.env['res.partner'].create({
                'name': self.x_name,
                'phone': self.x_phone,
                'industry_id': self.x_business_field.id if self.x_business_field else False,
                'category_id': category_ids,
            })

            self.x_customer_name = new_customer.id
            self.x_customer_code = new_customer.id

            return {
                'type': 'ir.actions.act_window',
                'name': 'Customer',
                'res_model': 'res.partner',
                'res_id': new_customer.id,
                'view_mode': 'form',
                'target': 'current',
                'context': {
                    'default_x_registration_code': self.x_registration_code,  # Điền sẵn mã phiếu đăng ký
                }
            }
        except Exception as e:
            # Log the error for debugging
            _logger.error('Error creating customer: %s', str(e))
            # Raise user-friendly error
            raise UserError(_('Could not create customer. Please check if all required fields are filled correctly.'))