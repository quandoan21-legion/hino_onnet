from odoo import models, fields, api, _

BID_AUTHORIZATION_STATE = [
    ('draft', 'Draft'),
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('cancel', 'Cancel'),
    ('win', 'Win'),
    ('lose', 'Lose'),
    ('signed', 'Signed'),
    ('completed', 'Completed'),
]

class BidAuthorization(models.Model):
    _name = 'bid.authorization'
    _description = 'Bid Authorization'

    state = fields.Selection(
        selection=BID_AUTHORIZATION_STATE,
        string='State',
        default='draft')

    request_code = fields.Char(string='Request Code', required=True, index='trigram', default=lambda self: _('New'))
    bid_package_name = fields.Char(string='Bid Package Name', required=True)
    area = fields.Text(string='Area')
    project_name = fields.Char(string='Project Name', required=True)
    request_date = fields.Date(string='Request Date')
    approved_date = fields.Date(string='Approved Date')
    bid_opening_time = fields.Date(string='Bid Opening Time')
    note = fields.Char(string='Note')
    authorization_letter_approve = fields.Binary(string='Authorization Letter Approve')
    investor_name = fields.Char(string='Investor Name', required=True)
    investor_address = fields.Char(string='Address', required=True)
    special_request = fields.Char(string='Special Request')
    date_of_authorization = fields.Date(string='Date of Authorization')
    send_authorization_to = fields.Char(string='Send Authorization To')
    attached_notice_file = fields.Binary(string='Attached Notice File')

    dealer_id = fields.Many2one('res.company', string='Dealer', required=True)
    # lead_code_id = fields.Many2one('crm.lead', string='Lead Code', required=True)

    bid_authorization_approve_history_ids = fields.One2many('bid.authorization.approve.history', 'bid_authorization_id', string='Bid Authorization Line')
    def action_submit(self):
        for record in self:
            # if record.create_uid == self.env.user:
            #     record.state = 'draft'
            record.state = 'pending'

    def action_approved(self):
        for record in self:
            # if record.create_uid == self.env.user:
            #     record.state = 'pending'
            record.state = 'approved'

    def action_rejected(self):
        for record in self:
            # if record.create_uid == self.env.user:
            #     record.state = 'pending'
            original_state = record.state
            record.state = 'rejected'
            return {
                'type': 'ir.actions.act_window',
                'name': 'Provide Reason',
                'res_model': 'bid.authorization.approve.history',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_reason': record.note, 
                            'default_bid_authorization_id': record.id,
                            'default_state_from': original_state,
                            'default_state_to': record.state,
                            'default_confirm_date': fields.Date.today()},            
            }
    
    def action_cancel(self):
        for record in self:
            original_state = record.state
            record.state = 'cancel'
            return {
                'type': 'ir.actions.act_window',
                'name': 'Provide Reason',
                'res_model': 'bid.authorization.approve.history',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_reason': record.note, 
                            'default_bid_authorization_id': record.id,
                            'default_state_from': original_state,
                            'default_state_to': record.state,
                            'default_confirm_date': fields.Date.today()},
            }
    
    def action_win(self):
        for record in self:
            record.state = 'win' 

    def action_lose(self):
        for record in self:
            record.state = 'lose'

    def action_signed(self):
        for record in self:
            record.state = 'signed'     

    def action_completed(self): 
        for record in self:
            record.state = 'completed'
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('request_code', _("New")) == _("New"):
                vals['request_code'] = self.env['ir.sequence'].next_by_code('bid.authorization') or _("New")
        return super().create(vals_list)
    
    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     if view_type == 'form':
    #         doc = etree.XML(res['arch'])
    #         for node in doc.xpath("//form"):
    #             if self.env.user.id != self.create_uid.id and self.state != 'draft':
    #                 node.set('readonly', '1')
    #         res['arch'] = etree.tostring(doc, encoding='unicode')
    #     return res