from odoo import models, fields, api, _


class SaleRequestRefuseWizard(models.TransientModel):
    _name = "sale.request.cancel.wizard"

    sale_request_id = fields.Many2one('sale.request', string="Sale Request", required=True)
    refuse_reason = fields.Text(string="Reason Rejection", required=True)

    def confirm_cancel(self):
        self.sale_request_id.write({
            'x_state': 'cancelled',
            'x_reason': self.refuse_reason
        })