from odoo import models, fields, api


class CustomLead(models.Model):
    _inherit = 'crm.lead'
    x_readonly_fields = fields.Boolean(
        compute="_compute_readonly_fields", store=True)
    name = fields.Char(string='Lead Name', required=True,
                       readonly=True, default="PCxxxxxx")
    # Notebook lines
    x_member_unit_ids = fields.One2many(
        'member.unit', 'lead_id', string='Member Unit')
    x_owned_team_car_line_ids = fields.One2many(
        'owned.team.car.line', 'lead_id', string='Owned Team Car Lines')
    x_customer_follow_up_ids = fields.One2many(
        'crm.follow.up', 'lead_id', string='Customer Follow-Up')
    x_partner_rank_id = fields.Many2one(
        'customer.rank', string='Rank', require=True)
    x_contact_person_ids = fields.One2many(
        'crm.lead.contact.person', 'lead_id', string='Contact')
    x_customer_status = fields.Selection(
        [
            ('person', 'Individual'),
            ('company', 'Company'),
            ('internal_hmv', 'Internal HMV')
        ],
        string="Customer Status",
        default='person'
    )
    x_partner_id = fields.Many2one(
        'res.partner', string='Customer', tracking=True, store=True)
    x_partner_name = fields.Char(
        string='Customer Name', store=True, tracking=True)
    x_website = fields.Char(string="Website", store=True, tracking=True)
    x_contact_address_complete = fields.Char(
        string="Contact Address", help="Customer's detailed address.", require=True)
    x_customer_type = fields.Selection(
        [('draft', 'Old Customer'), ('third_party', 'Third Party'),
         ('body_maker', 'Body Maker')],
        string='Third part/Body maker', default='draft', tracking=True
    )
    x_vat = fields.Char(
        string='Business Registration ID (Tax code)', tracking=True)
    x_identity_number = fields.Char(string='Identity Number', tracking=True)
    x_industry_id = fields.Many2one(
        'res.partner.industry', string='Industry', require=True)
    x_request_sale_3rd_barrels_id = fields.Many2one('third.party.registration',
                                                    string='Proposal to sell in Encroaching area/Third party/Body maker',
                                                    readonly=True,
                                                    domain="[ ('x_state', '=', 'approved')]")

    x_bidding_package = fields.Char(string='Bidding Package', tracking=True)
    x_purchase_type = fields.Selection(
        [('online_shopping', 'Online Shopping'),
         ('bidding', 'Bidding'), ('other', 'Other')],
        string='Purchase type', tracking=True, require=True
    )
    x_project = fields.Char(string='Project', tracking=True)
    x_estimated_time_of_bid_opening = fields.Date(
        string='Estimated time of bid opening', tracking=True)
    x_area = fields.Char(string='Area', tracking=True)
    x_service_contract = fields.Boolean(
        string='Service Contact', tracking=True, require=True)
    x_activity_area = fields.Char(string='Activity Area', tracking=True, require=True)
    x_dealer_id = fields.Many2one(
        'res.company',
        string='Dealer',
        readonly=True,
        compute="_compute_dealer_id",
        store=True
    )
    x_dealer_branch_id = fields.Many2one(
        'res.company',
        string='Dealer Branch',
        tracking=True,
        required=True,
        domain="[('parent_id', '!=', False)]"
    )
    x_sale_person_id = fields.Many2one('hr.employee', string='Sales Person', domain=[
                                       ('job_id.name', '=', 'Sales staff')], tracking=True, require=True)
    x_approaching_channel_id = fields.Many2one(
        'approach.channel', string='Approaching channels', tracking=True, require=True)
    x_state_id = fields.Many2one(
        'res.country.state', string="State/Province", require=True
    )

    x_vehicle_interest_ids = fields.One2many(
        'crm.lead.vehicle.interest.line',
        'lead_id',
        string='Customer interested vehicle'
    )

    x_status = fields.Selection([
        ('draft', 'Draft'),
        ('in progress', 'In Progress'),
        ('contract signed', 'Contract Signed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    @api.depends('x_status')
    def _compute_readonly_fields(self):
        for record in self:
            record.x_readonly_fields = record.x_status != 'draft'