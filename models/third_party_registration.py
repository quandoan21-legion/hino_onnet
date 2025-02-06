from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
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

    x_name = fields.Char(string='Unit Name', required=True)
    x_registration_code = fields.Char(string='Registration Code',  readonly=True)
    x_customer_name = fields.Many2one('res.partner', string='Customer Name', required=True)
    x_customer_code = fields.Many2one('res.partner', string='Customer Code', readonly=True)
    x_representative = fields.Many2one('res.partner', string='Representative', required=True)
    x_phone = fields.Char(string='Phone Number', required=True)
    x_business_field = fields.Many2one('res.partner.industry', string='Business Field')
    x_registration_type = fields.Many2one('res.partner.category', string='Registration Type')
    x_attach_files = fields.Binary(string='Attachment', attachment=True)
    x_ability_distribute_standards = fields.Boolean(string='Able to issue carton paper according to HMV standards')
    x_barrels_3rd_processes = fields.Boolean(string='The third unit processes barrels')
    x_unit_3rd_commercial = fields.Boolean(string='Commercial third unit')
    x_note = fields.Text(string='Reason for selling car')

    # One2many relation for multiple approvals
    x_approval_ids = fields.One2many('third.party.registration.approval', 'registration_id', string='Approvals')

    x_state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], default='draft', string='State')

    # Add field constraints
    @api.constrains('x_phone')
    def _check_phone(self):
        for record in self:
            if record.x_phone:
                # Check for duplicates
                duplicate = self.env['res.partner'].search([
                    ('phone', '=', record.x_phone),
                    ('id', '!=', record.x_customer_name.id)
                ], limit=1)
                if duplicate:
                    raise ValidationError(_('Phone number already exists for another customer!'))

    # Add file validation
    @api.constrains('x_attach_files')
    def _check_attachment_type(self):
        for record in self:
            if record.x_attach_files:
                # Implement PDF validation logic
                if not record.x_attach_files.mimetype == 'application/pdf':
                    raise ValidationError(_('Only PDF files are allowed!'))

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
            if self.x_registration_type:
                category_ids = [(4, self.x_registration_type.id)]

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
            }
        except Exception as e:
            # Log the error for debugging
            _logger.error('Error creating customer: %s', str(e))
            # Raise user-friendly error
            raise UserError(_('Could not create customer. Please check if all required fields are filled correctly.'))