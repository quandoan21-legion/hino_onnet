from odoo import models, fields, api


class VehicleInterest(models.Model):
    _name = 'crm.lead.vehicle.interest.line'

    lead_id = fields.Many2one('crm.lead', string='Sales Opportunity', required=True, ondelete='cascade', index=True)
    x_partner_code = fields.Many2one('res.partner', string='Customer Code', required=True)
    x_partner_name = fields.Char(string='Customer Name', required=True)
    x_address = fields.Text(string='Address', required=True)
    x_province_id = fields.Many2one('res.country.state', string='Province/City', required=True)
    # x_order_detail_3rd = fields.Many2one('order.detail.3rd', string='Third Party Order Details')
    # x_model_type_id = fields.Many2one('product.product', string='Vehicle Type', required=True)
    x_body_type_id = fields.Many2one('hino.body.type', string='Body Type', required=True)
    x_quantity = fields.Integer(string='Quantity', required=True)
    x_expected_implementation_time = fields.Date(string='Expected Delivery Date', required=True)
    x_expected_time_sign_contract = fields.Date(string='Expected Contract Signing Date', required=True)
    x_note = fields.Text(string='Note')

    @api.onchange('lead_id')
    def _onchange_lead_id(self):
        if self.lead_id:
            self.x_partner_code = self.lead_id.x_partner_id.id
            self.x_partner_name = self.lead_id.x_partner_name
            self.x_address = self.lead_id.x_contact_address_complete
            self.x_province_id = self.lead_id.x_state_id

