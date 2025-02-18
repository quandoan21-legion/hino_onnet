from odoo import models, fields, api

class CrmLeadReportWizard(models.TransientModel):
    _name = 'crm.lead.report'
    _description = 'CRM Lead Report'

    date_from = fields.Date(string="From Date")
    date_to = fields.Date(string="To Date")
    branch_id = fields.Many2one('res.partner', string="Branch/Agent")

    def action_print_report(self):
        domain = []
        if self.date_from:
            domain.append(('create_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('create_date', '<=', self.date_to))
        if self.branch_id:
            domain.append(('branch_id', '=', self.branch_id.id))
        
        leads = self.env['crm.lead'].search(domain)
        return self.env.ref('hino_onnet.action_report_custom_lead').report_action(leads)
