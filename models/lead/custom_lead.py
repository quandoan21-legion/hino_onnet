
import re

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CustomLead(models.Model):
    _inherit = 'crm.lead'

    x_readonly_fields = fields.Boolean(compute="_compute_readonly_fields", store=True)
    name = fields.Char(string='Lead Name', required=True, readonly=True, default="e.g PC00000xx")
    # Notebook lines
    x_member_line_ids = fields.One2many('member.line', 'lead_id', string='Member Lines')
    x_owned_team_car_line_ids = fields.One2many('owned.team.car.line', 'lead_id', string='Owned Team Car Lines')
    x_customer_follow_up_ids = fields.One2many('crm.follow.up', 'lead_id', string='Customer Follow-Up')
    # x_partner_rank_id = fields.Many2one('res.partner.rank', string='Rank')

    x_partner_rank_id = fields.Many2one('customer.rank', string='Rank')
    x_customer_rank = fields.Char(string='Customer Rank', related='x_partner_rank_id.rank_name', store=True)

    x_contact_person_ids = fields.One2many('crm.lead.contact.person', 'lead_id', string='Contact')
    x_customer_status = fields.Selection(
        [
            ('personal', 'Personal'),
            ('company', 'Company'),
            ('internal_hmv', 'Internal_HMV')
        ],
        string="Customer Status",
        default='personal'
    )
    x_partner_id = fields.Many2one('res.partner', string='Customer', tracking=True)
    x_partner_name = fields.Char(string='Customer Name', compute='_compute_partner_details', store=True, tracking=True)
    x_website = fields.Char(string="Website", store=True, tracking=True, compute='_compute_partner_details')
    x_contact_address_complete = fields.Char(string="Contact Address",help="Customer's detailed address.", compute="_compute_partner_details")

    # x_customer_id = fields.Many2one('res.partner', string='Customer')
    # x_customer_real_id = fields.Char(string='Customer ID', compute='_compute_customer_real_id', store=True, readonly=True)
    # x_customer_name = fields.Char(string='Customer Name')

    x_customer_type = fields.Selection(
        [('draft', 'Draft'), ('third_party', 'Third Party'), ('body_maker', 'Body Maker')],
        string='Third part/Body maker', default='draft', tracking=True
    )
    x_phone = fields.Integer(string='Phone number', tracking=True)
    x_email_from = fields.Char(string='Email', tracking=True)
    x_vat = fields.Char(string='Business registration number (Tax code)', tracking=True)
    x_identity_number = fields.Char(string='Citizen identification card', tracking=True)
    x_industry_id = fields.Many2one('res.partner.industry', string='Business Field')
    # x_request_sale_3rd_barrels_id = fields.Many2one('res.request.sale.3rd.barrels', string='Đề nghị bán lấn vùng/Bên thứ 3/Nhà đóng thùng', readonly=True)
    x_purchase_type = fields.Selection(
        [('online_shopping', 'Online Shopping'), ('bidding', 'Bidding'), ('other', 'Other')],
        string='Purchase type', tracking=True
    )
    x_bidding_package = fields.Char(string='Bidding Package', tracking=True)
    x_project = fields.Char(string='Project', tracking=True)
    x_estimated_time_of_bid_opening = fields.Date(string='Estimated time of bid opening', tracking=True)
    x_area = fields.Char(string='Area', tracking=True)
    x_service_contract = fields.Boolean(string='Service Contact', tracking=True)
    x_activity_area = fields.Char(string='Activity Area', tracking=True)
    x_dealer_id = fields.Many2one('res.partner', string='Dealer', readonly=True)
    x_dealer_branch_id = fields.Many2one('res.company', string='Dealer Branch', default=lambda self: self.env.company, tracking=True)
    x_sale_person_id = fields.Many2one('hr.employee', string='Sales Person', domain=[('job_id.name', '=', 'Sales staff')], tracking=True)
    x_approaching_channel_id = fields.Many2one('approach.channel', string='Approaching channels', tracking=True)
    x_state_id = fields.Many2one(
        'res.country.state', string="State/Province"
    )

    x_vehicle_interest_ids = fields.One2many(
        'crm.lead.vehicle.interest.line',
        'lead_id',
        string='Customer interested vehicle'
    )

    x_status = fields.Selection([
        ('draft', 'Draft'),
        ('contract signed', 'Contract Signed'),
        ('in progress','In Progress'),
        ('completed','Completed'),
        ('failed','Failed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    @api.depends('x_status')
    def _compute_readonly_fields(self):
        for record in self:
            record.x_readonly_fields = record.x_status != 'draft'
