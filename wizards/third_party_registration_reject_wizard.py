from odoo import fields, models


class ThirdPartyRegistrationRejectWizard(models.TransientModel):
    _name = 'third.party.registration.reject.wizard'
    _description = 'Rejection Reason Wizard'

    registration_id = fields.Many2one('third.party.registration', required=True)
    rejection_reason = fields.Text('Rejection Reason', required=True)

    def action_confirm_reject(self):
        self.ensure_one()
        if self.registration_id and self.rejection_reason:
            # Create approval log
            self.env['third.party.registration.approval'].create({
                'registration_id': self.registration_id.id,
                'x_approval_person': self.env.user.id,
                'x_department': self.env.user.employee_id.department_id.id if self.env.user.employee_id else False,
                'x_position': self.env.user.employee_id.job_id.id if self.env.user.employee_id else False,
                'x_previous_state': 'pending',
                'x_new_state': 'rejected',
                'x_note': self.rejection_reason,
            })

            self.registration_id.write({
                'x_state': 'rejected',
                'x_rejection_reason': self.rejection_reason
            })

            # Return form view for editing
            form_view_id = self.env.ref('hino_onnet.view_third_party_registration_form').id
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'third.party.registration',
                'res_id': self.registration_id.id,
                'view_mode': 'form',
                'views': [(form_view_id, 'form')],
                'target': 'current',
            }
        return {'type': 'ir.actions.act_window_close'}