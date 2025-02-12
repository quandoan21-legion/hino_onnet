from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

class VehicleInterestLineMethods(models.Model):
    _inherit = 'crm.lead.vehicle.interest.line'

    # @api.onchange('x_order_detail_3rd', 'x_partner_name')
    # def _onchange_fields(self):
    #     if self.x_order_detail_3rd:
    #         self.x_partner_name = self.x_order_detail_3rd.partner_id
    #         self.x_customer = self.x_order_detail_3rd.partner_id.name
    #         self.x_address = self.x_order_detail_3rd.partner_id.street
    #         self.x_province_id = self.x_order_detail_3rd.partner_id.state_id
    #         self.x_model_type_id = self.x_order_detail_3rd.model_type_id
    #         self.x_body_type_id = self.x_order_detail_3rd.body_type_id
    #
    #     elif self.x_partner_name:
    #         self.x_customer = self.x_partner_name.name
    #         self.x_address = self.x_partner_name.street or ''
    #         self.x_province_id = self.x_partner_name.state_id
    #

    @api.constrains('x_address', 'x_expected_implementation_time', 'x_expected_time_sign_contract')
    def _check_fields(self):
        for record in self:
            if not record.x_address or record.x_address.isspace():
                raise ValidationError("Address cannot contain only space and not null.")
            if not any(char.isdigit() for char in record.x_address) and not any(char.isalpha() for char in record.x_address):
                raise ValidationError("Address must contain both letters and numbers.")

            # if record.x_quantity <= 0:
            #     raise ValidationError("Quantity must be greater than 0 and a valid number.")

            if record.x_expected_implementation_time and record.x_expected_time_sign_contract:
                if record.x_expected_implementation_time < record.x_expected_time_sign_contract:
                    raise ValidationError("The expected delivery date cannot be earlier than the expected contract signing date.")

    @api.constrains('x_quantity')
    def _check_quantity(self):
        for record in self:
            try:
                quantity = float(record.x_quantity)
                if quantity <= 0:
                    raise ValidationError("Quantity must be greater than 0 and a valid number.")
            except (ValueError, TypeError):
                raise ValidationError("Quantity must be a valid number.")
