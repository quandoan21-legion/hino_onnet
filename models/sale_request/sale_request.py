from odoo import models, fields, api   

class SaleRequest(models.Model):
    _name = 'sale.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'x_request_date desc, x_request_code desc'
    
    x_request_code = fields.Char(
        string="Request Code",
        readonly=True,
        copy=False,
        default=lambda self: self._generate_request_code()
    )
  
    # x_request_dealer_id  = fields.Many2one('res.partner', string='Dealer', required=True, readonly=True, tracking=True, domain="[('is_dealer', '=', True)]")
    # x_dealer_branch_id = fields.Many2one('res.company', string='Dealer Branch', required=True, readonly=True, tracking=True, default=lambda self: self.env.company)
    x_customer_id = fields.Many2one('res.partner', string='Customer', required=False, tracking=True)
    x_customer_name = fields.Char(string='Customer Name', required=True, tracking=True)
    x_lead_code_id = fields.Many2one('crm.lead', string='Lead Code', tracking=True)
    x_customer_address = fields.Char(string='Customer Address', required=False, tracking=True)
    x_province_id  = fields.Many2one('res.country.state', string='Province', required=True, tracking=True)
    x_customer_region = fields.Many2one('sale.area', string='Customer Region', tracking=True, readonly=True, store=True, compute='_compute_customer_region_id')
    x_identitfication_id = fields.Char(string='Identification', required=True, tracking=True)
    x_business_registration_id = fields.Char(string='Business Registration', required=True, tracking=True)
    x_request_content_id = fields.Many2one('request.content', required=True, tracking=True)
    x_reason = fields.Char(string='Reason',tracking=True)
    x_old_customer =  fields.Boolean(string='Old Customer', store=True, tracking=True)
    x_customer_type = fields.Selection([
        ('out_of_area', 'Customer Out Of Area'),
        ('third_party', 'Third Party Customer'),
        ('box_packer', 'Box Packer'),
    ], string='Customer Type', required=True, tracking=True)
    x_state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('partial_sale', 'Partial Sale'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft',tracking=True) 
    x_request_date = fields.Date(string='Request Date', required=True, default=fields.Date.context_today, tracking=True)
    x_approve_date = fields.Date(string='Approve Date', readonly=True, default=fields.Date.context_today, tracking=True)
    x_expected_sale_date = fields.Date(string='Expected Sale Date', tracking=True) 
    x_expected_to_sign_contract = fields.Date(string='Expected To Sign Contract', tracking=True)
    x_attach_file = fields.Binary(string='Attach File', tracking=True)  
    x_attach_filename = fields.Char(string='Attach File Name', tracking=True)
    
    
    _sql_constraints = [
        ('unique_request_code', 'unique(x_request_code)', 'Request Code must be unique!'),
    ]
       
    
    
    