from odoo import models, fields, api

class OwnedTeamCarLine(models.Model):
    _inherit = 'owned.team.car.line'

    # x_partner_id = fields.Many2one('x.owned.car.line.report', string='Car Report')
