from odoo import models, fields, api


class VehicleInterest(models.Model):
    _name = 'crm.lead.vehicle.interest.line'

    lead_id = fields.Many2one('crm.lead', string='Sales Opportunity', required=True, ondelete='cascade', index=True)
    x_customer_type = fields.Selection(related="lead_id.x_customer_type", readonly=True)
    x_state = fields.Selection(related='lead_id.x_status', string='Status', readonly=True)
    x_partner_code = fields.Many2one('res.partner', string='Customer Code', required=True)
    x_partner_name = fields.Char(string='Customer Name', required=True)
    x_address = fields.Text(string='Address', required=True)
    x_province_id = fields.Many2one('res.country.state', string='Province/City', required=True)
    x_model_id = fields.Many2one('product.product', string='Vehicle Type', required=True)
    x_body_type_id = fields.Many2one('hino.body.type', string='Body Type', required=True)
    x_quantity = fields.Integer(string='Quantity', required=True)
    x_expected_implementation_time = fields.Date(string='Expected Delivery Date', required=True)
    x_expected_time_sign_contract = fields.Date(string='Expected Contract Signing Date', required=True)
    x_note = fields.Text(string='Note')
    sale_request_id = fields.Many2one('sale.request', string='Sale Request')
    sale_detail_ids = fields.Many2one('sale.detail', string='Sale Details')
    parent_sale_detail = fields.Many2one('sale.detail', string='Sale Detail',
                                         domain="[('sale_request_id', '=', sale_request_id)]")

    @api.model
    def create(self, vals):
        if 'x_partner_code' not in vals or not vals['x_partner_code']:
            lead = self.env['crm.lead'].browse(vals.get('lead_id'))
            vals['x_partner_code'] = lead.id
        return super(VehicleInterest, self).create(vals)

    def write(self, vals):
        for record in self:
            if 'x_partner_code' not in vals or not vals['x_partner_code']:
                vals['x_partner_code'] = record.lead_id.id
        return super(VehicleInterest, self).write(vals)

    @api.onchange('lead_id')
    def _onchange_lead_id(self):
        if self.lead_id:
            self.x_partner_code = self.lead_id.x_partner_id.id
            self.x_partner_name = self.lead_id.x_partner_name
            self.x_address = self.lead_id.x_contact_address_complete
            self.x_province_id = self.lead_id.x_state_id

    @api.onchange('lead_id.x_request_sale_3rd_barrels_id')
    def _onchange_x_request_sale_3rd_barrels_id(self):
        if self.lead_id and self.lead_id.x_request_sale_3rd_barrels_id:
            self.x_partner_code = self.lead_id.x_request_sale_3rd_barrels_id.x_customer_id.id
