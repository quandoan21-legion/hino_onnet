from odoo import fields, models

class ThirdPartyRegistrationRejectWizard(models.TransientModel):
    _name = 'third.party.registration.reject.wizard'
    _description = 'Rejection Reason Wizard'

    registration_id = fields.Many2one('third.party.registration', required=True)
    rejection_reason = fields.Text('Rejection Reason', required=True)

    def action_confirm_reject(self):
        self.ensure_one()
        if self.registration_id and self.rejection_reason:
            self.registration_id.write({
                'x_state': 'rejected',
                'x_note': self.rejection_reason
            })
            # Create approval log
            self.env['third.party.registration.approval'].create({
                'registration_id': self.registration_id.id,
                'x_approval_person': self.env.user.id,
                'x_previous_state': 'waiting_approval',
                'x_new_state': 'rejected',
            })
        return {'type': 'ir.actions.act_window_close'}