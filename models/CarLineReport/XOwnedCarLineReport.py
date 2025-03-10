from odoo import models, fields, api

class XOwnedCarLineReport(models.Model):
    _name = 'x.owned.car.line.report'
    _description = 'Owned Car Line Report'

    name = fields.Char(string='Report Name', required=True, default="Owned Car Line Report")
    x_owned_car_line_ids = fields.One2many(
        'owned.team.car.line', 'x_partner_id',
        string='Owned Team Car Lines', compute='_compute_owned_car_line_ids'
    )

    @api.depends('x_owned_car_line_ids')
    def _compute_owned_car_line_ids(self):
        """Fetch all owned.team.car.line records."""
        for record in self:
            record.x_owned_car_line_ids = self.env['owned.team.car.line'].search([])
