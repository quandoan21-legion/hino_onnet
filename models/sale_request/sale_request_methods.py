from odoo import models, fields,api, _
from odoo.exceptions import ValidationError
from datetime import datetime

class SaleRequestMethods(models.Model):
    _inherit = 'sale.request'

    # Override Methods
    @api.model
    def create(self, vals):
        if not vals.get('x_request_code'):
            vals['x_request_code'] = self.env['ir.sequence'].next_by_code('sale.request.sequence')
        return super(SaleRequestMethods, self).create(vals)

    def _generate_request_code(self):
        sequence = self.env['ir.sequence'].next_by_code('sale.request.sequence') or '/'
        return sequence
    
    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super().get_view(view_id, view_type, **options)
        if view_type == 'tree':
            if 'arch' in res:
                res['arch'] = res['arch'].replace('<tree>', '<tree create="false">')
        return res

    # Compute Methods
    @api.depends('x_province_id')
    def _compute_customer_region(self):
        for record in self:
            if record.province_id:
                record.customer_region = self.env['sale.area'].search([
                    ('province_ids', 'in', record.province_id.id)
                ], limit=1)

    @api.depends('x_customer_id', 'x_identification_id', 'x_business_registration')
    def _compute_old_customer(self):
        for record in self:
            record.x_old_customer = False
            if record.x_customer_id:
                record.x_old_customer = True
            elif record.x_identification_id:
                existing = self.env['res.partner'].search([
                    ('identification_id', '=', record.x_identification_id)
                ], limit=1)
                record.x_old_customer = bool(existing)
            elif record.x_business_registration:
                existing = self.env['res.partner'].search([
                    ('business_registration', '=', record.x_business_registration)
                ], limit=1)
            record.x_old_customer = bool(existing)

    @api.depends('x_sale_detail_ids.qty_done', 'x_sale_detail_ids.qty_confirmed')
    def _compute_sale_status(self):
        """Compute sale status based on quantities"""
        for record in self:
            if record.x_state not in ['approved', 'partial_sale', 'completed']:
                continue
                
            if record.x_sale_detail_ids:
                total_done = sum(record.x_sale_detail_ids.mapped('qty_done'))
                total_confirmed = sum(record.x_sale_detail_ids.mapped('qty_confirmed'))
                
                if total_done == 0:
                    continue
                elif total_done < total_confirmed:
                    record.x_state = 'partial_sale'
                elif total_done == total_confirmed:
                    record.x_state = 'completed'
    
    # Onchange Methods
    @api.onchange('x_customer_id')
    def _onchange_customer_id(self):
        if self.x_customer_id:
            self.x_customer_name = self.x_customer_id.name
            self.x_customer_address = self.x_customer_id.street
            self.x_province_id = self.x_customer_id.state_id
            # self.x_identification_id = self.x_customer_id.identification_id
            # self.x_business_registration = self.x_customer_id.business_registration
            lead = self.env['crm.lead'].search([
                ('partner_id', '=', self.x_customer_id.id)
            ], order="create_date desc", limit=1)
            self.x_lead_code_id = False

    @api.onchange('x_lead_code_id')
    def _onchange_lead_code_id(self):
        if self.x_lead_code_id:
            self.x_customer_name = self.x_lead_code_id.contact_name
            self.x_customer_address = self.x_lead_code_id.street
            self.x_province_id = self.x_lead_code_id.state_id
            self.x_customer_id = False
    
    @api.onchange('x_customer_type', 'x_province_id')
    def _check_region(self):
        if self.x_customer_type in ['third_party', 'box_packer']:
            if not self.x_province_id:
                return {'warning': {
                    'title': 'Warning',
                    'message': 'Province must be set for this customer type'
                }}
            
            allowed_regions = self.env['sale.area'].search([
                ('x_sales_area_detail_ids.x_code', '=', self.x_province_id.id)
            ])
            
            # if not allowed_regions:
            #     return {'warning': {
            #         'title': 'Warning',
            #         'message': 'Sales not allowed in this region for the selected customer type'
            #     }}
    
    # Validation Methods
    @api.constrains('x_expected_sale_date')
    def _check_expected_sale_date(self):
        for record in self:
            if record.x_expected_sale_date and record.x_expected_sale_date < fields.Date.today():
                raise ValidationError('Ngày dự kiến bán không được nhỏ hơn ngày hiện tại')

    @api.constrains('x_attach_file')
    def _check_file_type(self):
        for record in self:
            if record.x_attach_file and not record.x_attach_filename.lower().endswith('.pdf'):
                raise ValidationError('Chỉ cho phép đính kèm file PDF')

    # Constraint Methods
    @api.constrains('x_expected_sale_date')
    def _check_expected_sale_date(self):
        for record in self:
            if record.x_expected_sale_date and record.x_expected_sale_date < fields.Date.today():
                raise ValidationError('Expected sale date cannot be in the past')

    @api.constrains('x_attach_file', 'x_attach_filename')
    def _check_file_type(self):
        for record in self:
            if record.x_attach_file:
                if not record.x_attach_filename or not record.x_attach_filename.lower().endswith('.pdf'):
                    raise ValidationError('Only PDF files are allowed')

    @api.constrains('x_customer_type', 'x_province_id', 'x_end_customer_ids')
    def _check_sales_region(self):
        for record in self:
            if record.x_customer_type in ['third_party', 'box_packer']:
                if not record.x_end_customer_ids:
                    raise ValidationError(
                        'BÁN TRÁI VÙNG, YÊU CẦU NHẬP ĐỦ THÔNG TIN KHÁCH HÀNG CUỐI'
                    )

    # Action Methods
    def action_submit(self):
        self.ensure_one()
        self._check_region()
        self._check_sales_region()
        
        # Update state and date
        vals = {
            'x_state': 'pending',
            'x_request_date': fields.Date.today()
        }
        
        tracking_values = []
        for field, value in vals.items():
            old_value = self[field]

            if old_value != value:  # Chỉ track nếu có thay đổi
                field_record = self.env['ir.model.fields'].search([
                    ('model', '=', self._name),
                    ('name', '=', field)
                ], limit=1)

                if field_record: 
                    tracking_values.append((0, 0, {
                        'field_id': field_record.id, 
                        'old_value_char': str(old_value) if isinstance(old_value, (str, bool, int, float)) else None,
                        'new_value_char': str(value) if isinstance(value, (str, bool, int, float)) else None,
                        'old_value_float': old_value if isinstance(old_value, float) else None,
                        'new_value_float': value if isinstance(value, float) else None,
                    }))

                    
        self.write(vals)
        
        msg = f"""
            Request submitted for approval
            Submitted by: {self.env.user.name}
            Status: Draft -> Pending
            Date: {fields.Date.today()}
        """
        self.message_post(body=msg, tracking_value_ids=tracking_values)

    def action_approve(self):
        self.ensure_one()
        
        vals = {
            'x_state': 'approved',
            'x_approve_date': fields.Date.today()
        }
        
        # Update allowed dealer if customer exists
        # if self.x_customer_id:
        #     vals['x_allowed_dealer_id'] = self.x_request_dealer_id.id
            
        # tracking_values = []
        # for field, value in vals.items():
        #     tracking_values.append((0, 0, {
        #         'field': field,
        #         'old_value': self[field],
        #         'new_value': value
        #     }))
            
        self.write(vals)
        
        msg = f"""
            Request approved
            Approved by: {self.env.user.name}
            Status: Pending -> Approved
            Date: {fields.Date.today()}
        """
        self.message_post(body=msg, tracking_value_ids=tracking_values)

    def action_refuse(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nhập lý do từ chối',
            'res_model': 'sale.request.refuse.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_sale_request_id': self.id}
        }
        
    def action_cancel(self):
        for lead in self:
            if lead.x_state != 'draft':
                raise ValidationError(_("Only leads in Draft state can be cancelled."))
            
            if self.env.user != lead.create_uid:
                raise ValidationError(_("Only the creator of the lead can cancel it."))

            if not lead.x_cancellation_reason:
                raise ValidationError(_("Please provide a cancellation reason before cancelling."))

            tracking_values = self._track_subtype('x_state')
            msg = _("Lead cancelled. Reason: %s") % lead.x_cancellation_reason

            lead.write({
                'x_state': 'cancelled',
            })

            lead.message_post(body=msg, subtype_xmlid=tracking_values if tracking_values else False)

        return True