from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta
class SaleRequesSendMail(models.Model):
    _inherit = 'sale.request'

    def action_send_mail(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send Mail',
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'target': 'new',
            # 'context': {'default_email_to': self.email},
        }