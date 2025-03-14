import re
from datetime import datetime

from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError, UserError
from odoo.exceptions import UserError, warnings
import logging

logger = logging.getLogger(__name__)
class CustomLeadMethods(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def create(self, vals):
        if self._validate_customer_state(vals):
            vals['name'] = self._generate_pc_number()
            return super(CustomLeadMethods, self).create(vals)
        raise ValidationError("The customer state does not match with your Company State")

    def write(self, vals):
        if self._validate_customer_state(vals):
            vals['name'] = self._generate_pc_number()
            return super(CustomLeadMethods, self).write(vals)
        raise ValidationError("The customer state does not match with your Company State")

    @api.onchange('x_dealer_branch_id')
    def _onchange_dealer_branch_id(self):
        if self.x_dealer_branch_id:
            self.x_dealer_id = self.x_dealer_branch_id.parent_id if self.x_dealer_branch_id.parent_id else False

            self.x_state_id = self.x_dealer_branch_id.state_id if self.x_dealer_branch_id.state_id else False
        else:
            self.x_dealer_id = False
            self.x_state_id = False

    @api.depends('x_dealer_branch_id')
    def _compute_dealer_id(self):
        for record in self:
            record.x_dealer_id = record.x_dealer_branch_id.parent_id if record.x_dealer_branch_id else False
    # @api.model
    # def create(self, vals):
    #     if self._validate_customer_state(vals):
    #         vals['name'] = self._generate_pc_number()
    #         vals['x_partner_id'] = self._get_or_create_partner(vals)
    #         return super(CustomLeadMethods, self).create(vals)
    #     raise ValidationError("The customer state does not match with your Company State")
    # def write(self, vals):
    #     """ Prevent manual saving when status is not 'draft' """
    #     for record in self:
    #         if vals.get('x_partner_id'):
    #             raise exceptions.UserError("You cannot modify this lead ")
    #     return super(CustomLeadMethods, self).write(vals)
    @api.onchange('x_partner_id')
    def _onchange_x_partner_id(self):
        if self.x_partner_id:
            self.x_partner_name = self.x_partner_id.name
            self.x_contact_address_complete = self.x_partner_id.contact_address_complete
            self.x_website = self.x_partner_id.website
            self.phone = self.x_partner_id.phone
            self.email_from = self.x_partner_id.email
            self.x_customer_type = self.x_partner_id.x_customer_type if self.x_partner_id.x_customer_type in [
                'third_party', 'body_maker'] else 'draft'
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
            self.x_state_id = self.x_partner_id.x_state_id.id if self.x_partner_id.x_state_id else False
            self.x_dealer_branch_id = self.x_partner_id.x_dealer_branch_id.id if self.x_partner_id.x_dealer_branch_id else False

            related_leads = self.env['crm.lead'].search([
                ('x_partner_id', '=', self.x_partner_id.id)
            ])

            owned_cars = self.env['owned.team.car.line'].search([
                ('lead_id', 'in', related_leads.ids)
            ])

            if owned_cars:
                self.x_owned_team_car_line_ids = [(0, 0, {
                    'x_brand_name': car.x_brand_name,
                    'x_model_name': car.x_model_name,
                    'x_quantity': car.x_quantity,
                    'x_partner_id': car.x_partner_id.id,
                }) for car in owned_cars]
            else:
                self.x_owned_team_car_line_ids = [(5, 0, 0)]

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
        fiscal_year = self.env['account.fiscal.year'].search([], limit=1, order='date_from desc')
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
            'x_lead_id': vals.get('x_lead_id', 'Lead Id'),
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
            'x_allow_dealer_id': [(4, vals.get('x_dealer_branch_id'))] if vals.get('x_dealer_branch_id') else False,
            'x_state_id': vals.get('x_state_id'),
            'x_dealer_id': vals.get('x_dealer_id'),
            'x_dealer_branch_id': vals.get('x_dealer_branch_id'),
            'x_activity_area': vals.get('x_activity_area'),
            'x_service_contract': vals.get('x_service_contract'),
            'x_currently_rank_id': vals.get('x_partner_rank_id'),
        }
        return self.env['res.partner'].create(partner_vals)

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

    def action_mark_failed(self):
        self.write({'x_status': 'failed'})

    def action_mark_canceled(self):
        self.write({'x_status': 'cancelled'})

    def action_create_customer(self):
        for record in self:
            if not record.x_partner_id:
                vals = {
                    'x_lead_id': record.id,
                    'x_partner_name': record.x_partner_name,
                    'phone': record.phone,
                    'email_from': record.email_from,
                    'x_vat': record.x_vat,
                    'x_website': record.x_website,
                    'x_identity_number': record.x_identity_number,
                    'x_industry_id': record.x_industry_id.id,
                    'x_request_sale_3rd_barrels_id': record.x_request_sale_3rd_barrels_id,
                    'x_contact_address_complete': record.x_contact_address_complete,
                    'x_customer_status': record.x_customer_status,
                    'x_state_id': record.x_state_id.id if record.x_state_id else False,
                    'x_dealer_id': record.x_dealer_id.id if record.x_dealer_id else False,
                    'x_dealer_branch_id': record.x_dealer_branch_id.id if record.x_dealer_branch_id else False,
                    'x_activity_area': record.x_activity_area,
                    'x_service_contract': record.x_service_contract,
                    'x_partner_rank_id': record.x_partner_rank_id.id if record.x_partner_rank_id else False,
                }

                if not self._validate_customer_state(vals):
                    raise ValidationError("The customer state does not match with your Company State")

                record.x_partner_id = record._get_or_create_partner(vals)

        self.write({'x_status': 'in progress'})

    def _validate_customer_state(self, vals):
        dealer_branch_id = vals.get('x_dealer_branch_id')
        if dealer_branch_id:
            dealer_branch = self.env['res.company'].browse(dealer_branch_id)
            if dealer_branch.state_id.id != vals.get('x_state_id'):
                return False
        return True

    def action_view_third_party_registration(self):
        province_id = self.x_state_id.id
        logger.info(f"Default x_province_id (Before Returning Context): {province_id}")

        action = {
            'type': 'ir.actions.act_window',
            'name': 'sale.request.tree',
            'view_mode': 'form',
            'res_model': 'sale.request',
            'context': {
                'default_x_customer_id': self.x_partner_id.id,
                'default_x_request_dealer_id': self.x_dealer_id.id,
                'default_x_dealer_branch_id': self.x_dealer_branch_id.id,
                'default_x_customer_name': self.x_partner_name,
                'default_x_customer_address': self.x_contact_address_complete,
                'default_x_province_id': province_id,
                'default_x_identification_id': self.x_identity_number,
                'default_x_business_registration_id': self.x_vat,
                'default_x_lead_code_id': self.id,
                'default_x_request_date': fields.Date.context_today(self),
            }
        }
        return action


    @api.constrains('x_state_id', 'x_dealer_branch_id')
    def _check_customer_state(self):
        for record in self:
            if record.x_dealer_branch_id and record.x_dealer_branch_id.state_id:
                company_state = record.x_dealer_branch_id.state_id
                if company_state.id != record.x_state_id.id:

                    raise ValidationError(
                        "The selected state must match the state of the Dealer Branch Company.")

    # @api.constrains('x_partner_id')
    # def _check_unique_x_partner_id(self):
    #     for record in self:
    #         if record.x_partner_id:
    #             existing_lead = self.search([
    #                 ('x_partner_id', '=', record.x_partner_id.id),
    #                 ('id', '!=', record.id)  # Exclude the current record
    #             ], limit=1)
    #
    #             if existing_lead:
    #                 raise ValidationError("This customer is already assigned to another lead!")
    #

    def _prepare_contract_values(self):
        """Prepare values for crm.contract"""
        self.ensure_one()
        return {
            'customer_id': self.x_partner_id.id,
            'lead_code_id': self.id,
            'address': self.x_contact_address_complete,
            'customer_class_id': self.x_partner_rank_id.id,
            'purchase_type': self.x_purchase_type,
            'salesperson_id': self.x_sale_person_id.id,
            'dealer_id': self.x_dealer_id.id,
            'dealer_branch_id': self.x_dealer_branch_id.id,
        }

    def _prepare_contract_line_values(self, contract):
        """Prepare values for crm.contract.line"""
        contract_lines = []
        vehicle_interest = self.env['crm.lead.vehicle.interest.line'].search([('lead_id', '=', self.id)])
        for vehicle in vehicle_interest:
                contract_lines.append({
                    'contract_id': contract.id,
                    'line_end_customer_id': vehicle.x_partner_code.id,
                    'model_id':vehicle.x_model_id.id,
                    'line_barrel_type_id': vehicle.x_body_type_id.id,
                    'line_third_party_offer_ids': [(6, 0, vehicle.x_third_party_offer_ids.ids)],
                    'line_address': self.x_contact_address_complete,
                    'line_province_city_id': self.x_state_id.id,
                })
        return contract_lines if contract_lines else []

    def action_mark_draft(self):
        self.write({'x_status': 'draft'})

    def action_mark_cancel(self):
        self.write({'x_status': 'cancelled'})

    def action_create_contract(self):
        """Create contract and change X_status to contract_signed"""
        contract_obj = self.env['crm.contract']
        contract_line_obj = self.env['crm.contract.line']

        for lead in self:
            if not lead.x_partner_id:
                raise UserError("Need customer to create contact")

        # create crm.contract record
        contract_vals = lead._prepare_contract_values()
        contract = contract_obj.create(contract_vals)

        # create crm.contract.line record
        contract_line_vals = lead._prepare_contract_line_values(contract)
        if not contract_line_vals:
            raise UserError("No contract line values were generated. Check vehicle interests.")

        contract_line_obj.create(contract_line_vals)

        # Update lead status
        self.write({'x_status': 'contract signed'})

        return True