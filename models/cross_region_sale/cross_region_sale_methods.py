from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SaleRegionMethods(models.Model):
    _inherit = "sale.region"
    
    @api.constrains('release_time')
    def _check_release_time(self):
        for record in self:
            if record.release_time and record.release_time > fields.Date.today():
                raise ValidationError("Release Time cannot be in the future.")

    @api.constrains('dealer_branch_id')
    def _check_dealer_branch(self):
        for record in self:
            if not record.dealer_branch_id:
                raise ValidationError("Dealer Branch is required.")
