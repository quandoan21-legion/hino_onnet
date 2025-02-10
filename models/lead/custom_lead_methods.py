import re
from datetime import datetime

from odoo import models, api
from odoo.exceptions import ValidationError


class CustomLeadMethods(models.Model):
    _inherit = 'crm.lead'
    @api.depends('x_partner_id')
    def _compute_partner_details(self):
        for record in self:
            if record.x_partner_id:
                record.x_partner_name = record.x_partner_id.name
                record.x_contact_address_complete = record.x_partner_id.contact_address_complete
                record.x_website = record.x_partner_id.website
            else:
                record.x_partner_name = ''
                record.x_contact_address_complete = ''
                record.x_website = ''

    @api.onchange('x_partner_id')
    def _onchange_x_partner_id(self):
        if self.x_partner_id:
            self.x_phone = self.x_partner_id.phone
            self.x_email_from = self.x_partner_id.email
            self.x_vat = self.x_partner_id.vat
            self.x_identity_number = self.x_partner_id.x_identity_number
            self.x_industry_id = self.x_partner_id.industry_id
            self.x_service_contract = self.x_partner_id.service_contract if hasattr(self.x_partner_id,
                                                                                    'service_contract') else False
            self.x_activity_area = self.x_partner_id.activity_area if hasattr(self.x_partner_id,
                                                                              'activity_area') else ''

    @api.constrains('x_customer_status', 'x_identity_number', 'x_vat')
    def _check_customer_status_requirements(self):
        for record in self:
            if record.x_customer_status == 'personal' and not record.x_identity_number:
                raise ValidationError(
                    "For 'Individual', the field 'ID Number/Citizen Identification Number' is required.")
            if record.x_customer_status == 'company' and not record.x_vat:
                raise ValidationError("For 'Company', the field 'Business Registration Number (Tax Code)' is required.")

    @api.constrains('x_identity_number')
    def _check_identity_number(self):
        for record in self:
            if record.x_identity_number:
                if not re.match(r'^\d{9,13}$', record.x_identity_number):
                    raise ValidationError("The Identity number must contain from 9 to 13 digits.")

    def action_mark_failed(self):
        self.write({'x_status': 'failed'})

    def action_create_customer(self):
        self.write({'x_status': 'in progress'})

    def action_proposal(self):
        self.write({'x_status': 'in progress'})

    def action_cancel_lead(self):
        reason = self.env.context.get('cancel_reason')
        if not reason:
            raise ValidationError("A reason for cancellation is required.")
        self.write({'x_status': 'cancelled'})


@api.model
def create(self, values):
    # Get the fiscal year suffix (last 2 digits of current fiscal year)
    fiscal_year = self.env['account.fiscal.year'].search([], limit=1, order='date_from desc')

    if not fiscal_year:
        fiscal_year_suffix = str(datetime.now().year)[2:]
        print("Fiscal year not found, using current year suffix: " + fiscal_year_suffix)
    else:
        fiscal_year_suffix = str(fiscal_year.name)[2:]

    # Get the last record of crm.lead and extract the last 4 digits of the 'name' field
    last_lead = self.env['crm.lead'].search([], order='id desc', limit=1)
    if last_lead and last_lead.name:
        # Extract the last 4 digits from the 'name' field
        last_number = last_lead.name[-4:]
        try:
            new_number = str(int(last_number) + 1).zfill(4)  # Increment by 1 and pad with zeros
        except ValueError:
            new_number = '0001'  # Default value if last 4 digits cannot be converted
    else:
        # If no previous lead exists, start with '0001'
        new_number = '0001'

    # Combine the fiscal year suffix and the new sequence number to form the name
    pc_number = "PC" + fiscal_year_suffix + new_number

    # Set the name in the values dictionary
    values['name'] = pc_number

    # Call the parent class's create method to actually create the record
    return super(CustomLeadMethods, self).create(values)


@api.depends('x_partner_id')
def _compute_customer_name(self):
    for record in self:
        record.x_partner_name = record.x_partner_id.name if record.x_partner_id else ''


@api.onchange('x_partner_id')
def _onchange_x_partner_id(self):
    if self.x_partner_id:
        self.x_phone = self.x_partner_id.phone
        self.x_email_from = self.x_partner_id.email
        self.x_vat = self.x_partner_id.vat
        self.x_identity_number = self.x_partner_id.x_identity_number
        self.x_industry_id = self.x_partner_id.industry_id
        self.x_service_contract = self.x_partner_id.service_contract if hasattr(self.x_partner_id,
                                                                                'service_contract') else False
        self.x_activity_area = self.x_partner_id.activity_area if hasattr(self.x_partner_id, 'activity_area') else ''


# @api.depends('x_customer_id')
# def _compute_customer_real_id(self):
#     for record in self:
#         record.x_customer_real_id = str(record.x_customer_id.id) if record.x_customer_id else ''
#         record.x_customer_name = record.x_customer_id.name if record.x_customer_id else ''


# @api.onchange('partner_id')
# def _onchange_partner_id(self):
#     if self.partner_id:
#         self.x_identity_number = self.partner_id.identity_number
#         self.x_vat = self.partner_id.vat_number:
@api.constrains('x_customer_status', 'x_identity_number', 'x_vat')
def _check_customer_status_requirements(self):
    for record in self:
        if record.x_customer_status == 'personal' and not record.x_identity_number:
            raise ValidationError("For 'Individual', the field 'ID Number/Citizen Identification Number' is required.")
        if record.x_customer_status == 'company' and not record.x_vat:
            raise ValidationError("For 'Company', the field 'Business Registration Number (Tax Code)' is required.")


@api.constrains('x_identity_number')
def _check_identity_number(self):
    for record in self:
        if record.x_identity_number:
            if not re.match(r'^\d{9,13}$', record.x_identity_number):
                raise models.ValidationError("The Identity number must contain from 9 to 13 digits.")


@api.onchange('state')
def _onchange_state(self):
    if self.state != 'draft':
        self.salesperson_id = False


def action_mark_failed(self):
    self.write({'x_status': 'failed'})


def action_create_customer(self):
    self.write({'x_status': 'in progress'})


def action_proposal(self):
    self.write({'x_status': 'in progress'})


def action_cancel_lead(self):
    reason = self.env.context.get('cancel_reason')
    if not reason:
        raise ValidationError("A reason for cancellation is required.")
    self.write({'x_status': 'cancelled'})
