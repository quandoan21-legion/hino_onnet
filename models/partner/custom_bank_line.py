from odoo import models, fields, api

class CustomBankLine(models.Model):
    _name = 'bank.line'
    _description = 'Bank Line'

    x_partner_id = fields.Many2one('res.partner', string='Partner')
    x_branch = fields.Char(string="Branch")
    acc_number = fields.Many2one(
        'res.partner.bank',
        string='Account Number',
        context={'show_acc_number_only': True}
    )
    bank_id = fields.Many2one('res.bank', string='Bank', compute='_compute_bank_id', store=True)

    @api.depends('acc_number')
    def _compute_bank_id(self):
        for record in self:
            record.bank_id = record.acc_number.bank_id.id if record.acc_number else False
