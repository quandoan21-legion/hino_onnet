from odoo import models, api
from odoo.exceptions import ValidationError


class VehicleInterestLineMethods(models.Model):
    _inherit = 'crm.lead.vehicle.interest.line'

    @api.constrains('x_address', 'x_expected_implementation_time', 'x_expected_time_sign_contract')
    def _check_fields(self):
        for record in self:
            if not record.x_address or record.x_address.isspace():
                raise ValidationError("The address in the Customer Follow-up history form cannot contain only space.")
            if not any(char.isdigit() for char in record.x_address) and not any(char.isalpha() for char in record.x_address):
                raise ValidationError(
                    "The address in the Customer Follow-up history form must contain both letters and numbers.")
            if record.x_expected_implementation_time and record.x_expected_time_sign_contract:
                if record.x_expected_implementation_time < record.x_expected_time_sign_contract:
                    raise ValidationError(
                        "The expected delivery date cannot be earlier than the expected contract signing date in the Customer Follow-up history form.")

    @api.constrains('x_quantity')
    def _check_quantity(self):
        for record in self:
            try:
                quantity = float(record.x_quantity)
                if quantity <= 0:
                    raise ValidationError(
                        "Vehicle quantity for customer ({})'s vehicle must be greater than 0 and a valid number.".format(
                            record.x_partner_name
                        ))
            except (ValueError, TypeError):
                raise ValidationError("Quantity must be a valid number.")

    @api.model
    def create(self, vals):
        lead = self.env['crm.lead'].browse(vals.get('lead_id'))
        if lead and lead.x_status != 'draft':
            raise ValidationError(
                "You cannot create a new vehicle interest line because this lead form is not in DRAFT status.")
        return super(VehicleInterestLineMethods, self).create(vals)

    @api.model
    def write(self, vals):
        for record in self:
            if record.lead_id.x_status != 'draft':
                raise ValidationError(
                    "You cannot edit the vehicle interest line because this lead form is not in DRAFT status.")
        return super(VehicleInterestLineMethods, self).write(vals)
