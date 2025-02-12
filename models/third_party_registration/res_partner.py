from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def action_create_third_party_registration(self):
        """Open third party registration form with pre-filled data"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': '3rd Unit Register/Packaging House',
            'res_model': 'third.party.registration',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_x_customer_name': self.id,
                'default_x_customer_code': self.id,
                'default_x_phone': self.id if self.phone else False,
            }
        }