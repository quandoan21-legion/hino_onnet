from odoo import models, fields, api


class CrmLeadReportWizard(models.TransientModel):
    _name = 'crm.lead.report'
    _description = 'CRM Lead Report'

    date_from = fields.Date(string="From Date")
    date_to = fields.Date(string="To Date")
    x_dealer_id = fields.Many2one(
        'res.users', string="Dealer", default=lambda self: self.env.user, readonly=True)
    x_branch_id = fields.Many2one(
        'res.company', string="Branch", default=lambda self: self.env.company, readonly=True)

    def action_print_report(self):
        domain = []
        if self.date_from:
            domain.append(('create_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('create_date', '<=', self.date_to))
        if self.x_dealer_id:
            domain.append(('x_dealer_id', '=', self.x_dealer_id.id))
        if self.x_branch_id:
            domain.append(('x_dealer_branch_id', '=', self.x_branch_id.id))

        leads = self.env['crm.lead'].search(domain)
        return self.env.ref('hino_onnet.action_report_custom_lead').report_action(leads.ids)


class ReportCrmLead(models.AbstractModel):
    _name = 'report.hino_onnet.custom_lead_report_template'
    _description = 'CRM Lead Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['crm.lead'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'crm.lead',
            'docs': docs,
        }
