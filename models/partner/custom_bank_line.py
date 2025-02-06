from odoo import models, fields, api

class CustomLeadLine(models.Model):
    _name = 'bank.line'

    x_partner_id = fields.Many2one('res.partner', string='Partner')
    x_bank_id = fields.Many2one('res.partner.bank', string='Bank')
    x_branch = fields.Char(string="Branch")
    x_acc_number = fields.Many2one('res.partner.bank', string="Account Number")