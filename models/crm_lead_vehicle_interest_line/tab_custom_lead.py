from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class VehicleInterest(models.Model):
    _name = 'crm.lead.vehicle.interest.line'

    lead_id = fields.Many2one('crm.lead', string='Sales Opportunity', required=True, ondelete='cascade', index=True)
    x_customer_type = fields.Selection(related="lead_id.x_customer_type", readonly=True)
    x_state = fields.Selection(related='lead_id.x_status', string='Status', readonly=True)
    x_partner_code = fields.Many2one('res.partner', string='Customer Code', required=True)
    x_partner_name = fields.Char(string='Customer Name', required=True)
    x_address = fields.Text(string='Address', required=True)
    x_province_id = fields.Many2one('res.country.state', string='Province/City', required=True)
    x_model_id = fields.Many2one('product.product', string='Model', required=True)
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
    @api.model
    def create(self, vals):
        _logger.info(f"Creating new Vehicle Interest with values: {vals}")

        if 'x_partner_code' not in vals or not vals['x_partner_code']:
            lead = self.env['crm.lead'].browse(vals.get('lead_id'))
            if lead:
                _logger.info(
                    f"Found Lead: {lead.id}, Setting x_partner_code to: {lead.x_partner_id.id if lead.x_partner_id else 'None'}")
                vals['x_partner_code'] = lead.x_partner_id.id if lead.x_partner_id else False
            else:
                _logger.warning("Lead not found, x_partner_code not set.")

        return super(VehicleInterest, self).create(vals)

    def write(self, vals):
        _logger.info(f"Updating Vehicle Interest {self.id} with values: {vals}")

        for record in self:
            if 'x_partner_code' not in vals or not vals['x_partner_code']:
                vals['x_partner_code'] = record.lead_id.x_partner_id.id if record.lead_id.x_partner_id else False
                _logger.info(f"Updating x_partner_code for {record.id} to {vals['x_partner_code']}")

        return super(VehicleInterest, self).write(vals)

    @api.onchange('lead_id')
    def _onchange_lead_id(self):
        _logger.info(f"Triggered _onchange_lead_id for record ID: {self.id}")
        if self.lead_id:
            _logger.info(
                f"Lead ID: {self.lead_id.id}, Partner ID: {self.lead_id.x_partner_id.id if self.lead_id.x_partner_id else 'None'}")
            self.x_partner_code = self.lead_id.x_partner_id.id
            self.x_partner_name = self.lead_id.x_partner_name
            self.x_address = self.lead_id.x_contact_address_complete
            self.x_province_id = self.lead_id.x_state_id
        else:
            _logger.warning("lead_id is not set, skipping update.")

    @api.onchange('lead_id.x_request_sale_3rd_barrels_id')
    def _onchange_x_request_sale_3rd_barrels_id(self):
        if self.lead_id and self.lead_id.x_request_sale_3rd_barrels_id:
            self.x_partner_code = self.lead_id.x_request_sale_3rd_barrels_id.x_customer_id.id
