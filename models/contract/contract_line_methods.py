from odoo import models, fields, api
from datetime import datetime

class CRMContractMethods(models.Model):
    _inherit = 'crm.contract'

    @api.model
    def create(self, vals):
        # Get the current fiscal year
        fiscal_year = self.env['account.fiscal.year'].search([], order="date_from desc", limit=1)
        year_suffix = fiscal_year.name[-2:] if fiscal_year else datetime.today().year % 100

        sequence = self.env['ir.sequence'].next_by_code('crm.contract') or "0001"
        vals["contract_code"] = f"C0{year_suffix}{sequence}"

        return super().create(vals)
