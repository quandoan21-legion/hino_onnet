import re
from datetime import datetime

from odoo import models, api
from odoo.exceptions import ValidationError


class CustomLeadMethods(models.Model):
    _inherit = 'crm.lead'

    @api.onchange('x_partner_id')
    def _onchange_x_partner_id(self):
        if self.x_partner_id:
            self.x_partner_name = self.x_partner_id.name
            self.x_contact_address_complete = self.x_partner_id.contact_address_complete
            self.x_website = self.x_partner_id.website
            self.phone = self.x_partner_id.phone
            self.email_from = self.x_partner_id.email
            self.x_customer_type = self.x_partner_id.x_customer_type
            vat = self.x_partner_id.vat or ''
            business_reg_id = self.x_partner_id.x_business_registration_id or ''
            self.x_vat = f"{vat} / {business_reg_id}".strip(" /")
            self.x_identity_number = self.x_partner_id.x_identity_number
            self.x_industry_id = self.x_partner_id.x_industry_id
            self.x_service_contract = self.x_partner_id.x_service_contract
            self.x_request_sale_3rd_barrels_id = self.x_partner_id.x_register_sale_3rd_id
            self.x_activity_area = self.x_partner_id.x_activity_area
            self.x_state_id = self.x_partner_id.x_state_id
            self.x_dealer_id = self.x_partner_id.x_dealer_id
            self.x_dealer_branch_id = self.x_partner_id.x_dealer_branch_id
            self.x_partner_rank_id = self.x_partner_id.x_currently_rank_id
            self.x_customer_status = 'company' if self.x_partner_id.company_type == 'company' else 'person'
            self.x_contact_address_complete = self.x_partner_id.x_contact_address

    @api.constrains('x_customer_status', 'x_identity_number', 'x_vat')
    def _check_customer_status_requirements(self):
        for record in self:
            if record.x_customer_status == 'person' and not record.x_identity_number:
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
    def create(self, vals):
        print("+++++++++++++++++++++++++++++++++++++++++++++++=")
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
        vals['name'] = pc_number

        domain = []
        
        if vals.get('x_vat'):
            domain.append(('x_business_registration_id', '=', vals['x_vat']))
        if vals.get('x_identity_number'):
            domain.append(('x_identity_number', '=', vals['x_identity_number']))

        existing_partner = None
        if domain:
            existing_partner = self.env['res.partner'].search(domain, limit=1)

        if existing_partner:
            vals['x_partner_id'] = existing_partner.id
        else:
            partner_vals = {
                'name': vals.get('x_partner_name', 'Unnamed Customer'),
                'x_name': vals.get('x_partner_name'),
                'phone': vals.get('phone'),
                'email': vals.get('email_from'),
                'vat': vals.get('x_vat'),
                'website': vals.get('x_website'),
                'x_business_registration_id': vals.get('x_vat'),
                'x_identity_number': vals.get('x_identity_number'),
                'x_industry_id': vals.get('x_industry_id'),
                'x_register_sale_3rd_id': vals.get('x_request_sale_3rd_barrels_id'),
                'x_contact_address': vals.get('x_contact_address_complete'),
                'company_type': 'company' if vals.get('x_customer_status') == 'company' else 'person',
                'x_state_id': vals.get('x_state_id'),
                'x_dealer_id': vals.get('x_dealer_id'),
                'x_dealer_branch_id': vals.get('x_dealer_branch_id'),
                'x_activity_area': vals.get('x_activity_area'),
                'x_service_contract': vals.get('x_service_contract'),   
                'x_currently_rank_id': vals.get('x_partner_rank_id'),
            }

            new_partner = self.env['res.partner'].create(partner_vals)
            vals['x_partner_id'] = new_partner.id

        return super(CustomLeadMethods, self).create(vals)



    @api.depends('x_partner_id')
    def _compute_customer_name(self):
        for record in self:
            record.x_partner_name = record.x_partner_id.name if record.x_partner_id else ''

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
            if record.x_customer_status == 'person' and not record.x_identity_number:
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



    def action_cancel_lead(self):
        reason = self.env.context.get('cancel_reason')
        if not reason:
            raise ValidationError("A reason for cancellation is required.")
        self.write({'x_status': 'cancelled'})

    def action_view_third_party_registration(self):
        return {
            'type': 'ir.actions.act_window',
            'name': '3rd Party/Body Maker Registration',
            'view_mode': 'tree,form',
            'res_model': 'third.party.registration',
        }
