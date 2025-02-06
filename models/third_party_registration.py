from odoo import models, fields, api

class ThirdPartyRegistration(models.Model):
    _name = 'third.party.registration'
    _description = 'Third Party/Packaging House Registration'
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

    @api.model
    def create(self, vals):
        if not vals.get('x_registration_code'):
            vals['x_registration_code'] = self.env['ir.sequence'].next_by_code('third.party.registration.sequence')
        return super(ThirdPartyRegistration, self).create(vals)

    def action_submit(self):
        self.write({'x_state': 'waiting_approval'})

    def action_confirm(self):
        self.write({'x_state': 'approved'})

    def action_refuse(self):
        self.write({'x_state': 'rejected'})

    def action_cancel(self):
        self.write({'x_state': 'cancelled'})

    def action_create_customer(self):
        """ Create a new customer based on the registration details. """
        new_customer = self.env['res.partner'].create({
            'name': self.x_name,
            'phone': self.x_phone,
            'industry_id': self.x_business_field.id,
            'category_id': [(6, 0, [self.x_registration_type.id])],
        })
        self.x_customer_name = new_customer.id
        self.x_customer_code = new_customer.id  # Assuming customer code is the same as partner ID
        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer',
            'res_model': 'res.partner',
            'res_id': new_customer.id,
            'view_mode': 'form',
            'target': 'current',
        }