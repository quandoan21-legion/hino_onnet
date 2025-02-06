from odoo import fields, models, api
from odoo.exceptions import ValidationError


class CustomerRank(models.Model):
    _name = 'customer.rank'
    _description = 'Customer Rank'

    rank_name = fields.Char(string='Rank Name', required=True)

    # Override display_name to show rank_name instead of the default name
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.rank_name))
        return result
    min_hino_vehicles = fields.Integer(string='Minimum Hino Vehicles', required=True)
    max_hino_vehicles = fields.Integer(string='Maximum Hino Vehicles', required=True)
    min_owned_vehicles = fields.Integer(string='Minimum Owned Vehicles', required=True)
    max_owned_vehicles = fields.Integer(string='Maximum Owned Vehicles', required=True)

    @api.constrains('min_hino_vehicles', 'max_hino_vehicles', 'min_owned_vehicles', 'max_owned_vehicles')
    def _check_vehicle_ranges(self):
        for record in self:
            # Check if min values are less than max values within the same record
            if record.min_hino_vehicles > record.max_hino_vehicles:
                raise ValidationError("Minimum Hino Vehicles cannot be greater than Maximum Hino Vehicles.")

            if record.min_owned_vehicles > record.max_owned_vehicles:
                raise ValidationError("Minimum Owned Vehicles cannot be greater than Maximum Owned Vehicles.")

            if record.max_hino_vehicles > record.max_owned_vehicles:
                raise ValidationError("Maximum Hino Vehicles cannot be greater than Maximum Owned Vehicles.")

            if record.min_hino_vehicles > record.min_owned_vehicles:
                raise ValidationError("Minimum Hino Vehicles cannot be greater than Minimum Owned Vehicles.")

            # Check for overlapping with existing records
            existing_ranks = self.env['customer.rank'].search([
                ('id', '!=', record.id),  # Exclude the current record in case of update
                '|', '|', '|',
                '&', ('min_hino_vehicles', '<=', record.max_hino_vehicles),
                ('max_hino_vehicles', '>=', record.min_hino_vehicles),
                '&', ('min_owned_vehicles', '<=', record.max_owned_vehicles),
                ('max_owned_vehicles', '>=', record.min_owned_vehicles),
                '&', ('max_hino_vehicles', '>=', record.min_hino_vehicles),
                ('min_hino_vehicles', '<=', record.max_hino_vehicles),
                '&', ('max_owned_vehicles', '>=', record.min_owned_vehicles),
                ('min_owned_vehicles', '<=', record.max_owned_vehicles),
            ])

            if existing_ranks:
                raise ValidationError(
                    "The vehicle range overlaps with another existing rank. Please adjust the values to avoid conflicts.")
