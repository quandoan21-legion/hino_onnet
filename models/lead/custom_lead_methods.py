import re
from datetime import datetime

from odoo import models, api
from odoo.exceptions import ValidationError


class CustomLeadMethods(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def create(self, vals):
        if self._validate_customer_state(vals):
            vals['name'] = self._generate_pc_number()
            vals['x_partner_id'] = self._get_or_create_partner(vals)
            return super(CustomLeadMethods, self).create(vals)
        raise ValidationError(
            "The customer state does not match with your Company State")

    @api.onchange('x_partner_id')
    def _onchange_x_partner_id(self):
        if self.x_partner_id:
            self.x_partner_name = self.x_partner_id.name
            self.x_contact_address_complete = self.x_partner_id.contact_address_complete
            self.x_website = self.x_partner_id.website
            self.phone = self.x_partner_id.phone
            self.email_from = self.x_partner_id.email

            if self.x_partner_id.x_customer_type in ['third_party', 'body_maker']:
                self.x_customer_type = self.x_partner_id.x_customer_type
            else:
                self.x_customer_type = 'draft'

            vat = self.x_partner_id.vat or ''
            business_reg_id = self.x_partner_id.x_business_registration_id or ''
            self.x_vat = self.x_partner_id.x_business_registration_id
            self.x_identity_number = self.x_partner_id.x_identity_number
            self.x_industry_id = self.x_partner_id.x_industry_id
            self.x_service_contract = self.x_partner_id.x_service_contract
            self.x_request_sale_3rd_barrels_id = self.x_partner_id.x_register_sale_3rd_id
            self.x_activity_area = self.x_partner_id.x_activity_area
            self.x_dealer_id = self.x_partner_id.x_dealer_id
            self.x_partner_rank_id = self.x_partner_id.x_currently_rank_id
            self.x_customer_status = 'company' if self.x_partner_id.company_type == 'company' else 'person'
            self.x_contact_address_complete = self.x_partner_id.x_contact_address

    @api.constrains('x_customer_type', 'x_partner_id')
    def _validate_customer_type(self):
        for record in self:
            if record.x_partner_id and record.x_partner_id.x_customer_type in ['third_party', 'body_maker'] and record.x_customer_type == 'draft':
                raise ValidationError(
                    "This customer is a Third Party/Body Maker and cannot be switched back to Draft.")

    @api.constrains('x_customer_status', 'x_identity_number', 'x_vat')
    def _check_customer_status_requirements(self):
        for record in self:
            if record.x_customer_status == 'person' and not record.x_identity_number:
                raise ValidationError(
                    "For 'Individual', the field 'ID Number/Citizen Identification Number' is required.")
            if record.x_customer_status == 'company' and not record.x_vat:
                raise ValidationError(
                    "For 'Company', the field 'Business Registration Number (Tax Code)' is required.")

    @api.constrains('x_identity_number')
    def _check_identity_number(self):
        for record in self:
            if record.x_identity_number:
                if not re.match(r'^\d{9,13}$', record.x_identity_number):
                    raise ValidationError(
                        "The Identity number must contain from 9 to 13 digits.")

    def action_mark_failed(self):
        self.write({'x_status': 'failed'})

    def action_proposal(self):
        self.write({'x_status': 'in progress'})

    def action_cancel_lead(self):
        reason = self.env.context.get('cancel_reason')
        if not reason:
            raise ValidationError("A reason for cancellation is required.")
        self.write({'x_status': 'cancelled'})

    def _generate_pc_number(self):
        fiscal_year_suffix = self._get_fiscal_year_suffix()
        new_number = self._get_new_sequence_number()
        return "PC" + fiscal_year_suffix + new_number

    def _get_fiscal_year_suffix(self):
        fiscal_year = self.env['account.fiscal.year'].search(
            [], limit=1, order='date_from desc')
        if not fiscal_year:
            return str(datetime.now().year)[2:]
        return str(fiscal_year.name)[2:]

    def _get_new_sequence_number(self):
        last_lead = self.env['crm.lead'].search([], order='id desc', limit=1)
        if last_lead and last_lead.name:
            last_number = last_lead.name[-4:]
            try:
                return str(int(last_number) + 1).zfill(4)
            except ValueError:
                return '0001'
        return '0001'

    def _get_or_create_partner(self, vals):
        domain = self._build_partner_search_domain(vals)
        existing_partner = self.env['res.partner'].search(
            domain, limit=1) if domain else None
        if existing_partner:
            return existing_partner.id
        return self._create_new_partner(vals).id

    def _build_partner_search_domain(self, vals):
        domain = []
        if vals.get('x_vat'):
            domain.append(('x_business_registration_id', '=', vals['x_vat']))
        if vals.get('x_identity_number'):
            domain.append(('x_identity_number', '=',
                           vals['x_identity_number']))
        return domain

    def _create_new_partner(self, vals):
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
        partner = self.env['res.partner'].create(partner_vals)
        partner.write({'x_lead_id': vals.get('id')})
        return

    @api.constrains('x_customer_status', 'x_identity_number', 'x_vat')
    def _check_customer_status_requirements(self):
        for record in self:
            if record.x_customer_status == 'person' and not record.x_identity_number:
                raise ValidationError(
                    "For 'Individual', the field 'ID Number/Citizen Identification Number' is required.")
            if record.x_customer_status == 'company' and not record.x_vat:
                raise ValidationError(
                    "For 'Company', the field 'Business Registration Number (Tax Code)' is required.")

    @api.constrains('x_identity_number')
    def _check_identity_number(self):
        for record in self:
            if record.x_identity_number:
                if not re.match(r'^\d{9,13}$', record.x_identity_number):
                    raise models.ValidationError(
                        "The Identity number must contain from 9 to 13 digits.")

    # @api.onchange('state')
    # def _onchange_state(self):
    #     if self.state != 'draft':
    #         self.salesperson_id = False

    def action_mark_failed(self):
        self.write({'x_status': 'failed'})

    def action_create_customer(self):
        self._check_customer_state()
        self.write({'x_status': 'in progress'})

    def _validate_customer_state(self, vals):
        dealer_branch_id = vals.get('x_dealer_branch_id')
        if dealer_branch_id:
            dealer_branch = self.env['res.company'].browse(dealer_branch_id)
            if dealer_branch.state_id.id != vals.get('x_state_id'):
                return False
        return True

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

    @api.constrains('x_state_id', 'x_dealer_branch_id')
    def _check_customer_state(self):
        for record in self:
            if record.x_dealer_branch_id and record.x_dealer_branch_id.state_id:
                company_state = record.x_dealer_branch_id.state_id
                if company_state.id != record.x_state_id.id:
                    raise ValidationError(
                        "The selected state must match the state of the Dealer Branch Company.")

    @api.constrains('x_partner_id')
    def _check_unique_x_partner_id(self):
        for record in self:
            if record.x_partner_id:
                existing_lead = self.search([
                    ('x_partner_id', '=', record.x_partner_id.id),
                    ('id', '!=', record.id)  # Exclude the current record
                ], limit=1)

                if existing_lead:
                    raise ValidationError(
                        "This customer is already assigned to another lead!")
