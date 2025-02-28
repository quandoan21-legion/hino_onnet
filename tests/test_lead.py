from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError

class TestCustomLead(TransactionCase):

    def setUp(self):
        super(TestCustomLead, self).setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'company_type': 'company',
            'vat': '123456789',
            'x_identity_number': '987654321',
        })
        self.dealer_branch = self.env['res.company'].create({
            'name': 'Test Dealer Branch',
        })
        self.lead = self.env['crm.lead'].create({
            'x_partner_id': self.partner.id,
            'x_partner_name': self.partner.name,
            'x_vat': self.partner.vat,
            'x_identity_number': self.partner.x_identity_number,
            'x_dealer_branch_id': self.dealer_branch.id,
            'x_status': 'draft',
        })

    def test_create_lead(self):
        """Test lead creation with valid data"""
        self.assertEqual(self.lead.x_status, 'draft')
        self.assertEqual(self.lead.x_partner_id, self.partner)
        self.assertEqual(self.lead.x_vat, '123456789')

    def test_identity_number_constraint(self):
        """Test identity number validation"""
        with self.assertRaises(ValidationError):
            self.lead.write({'x_identity_number': '123'})  # Invalid ID (too short)
        with self.assertRaises(ValidationError):
            self.lead.write({'x_identity_number': '123456789012345'})  # Too long

    def test_customer_status_validation(self):
        """Ensure company requires VAT and person requires ID number"""
        self.lead.write({'x_customer_status': 'person', 'x_identity_number': ''})
        with self.assertRaises(ValidationError):
            self.lead._check_customer_status_requirements()
        self.lead.write({'x_customer_status': 'company', 'x_vat': ''})
        with self.assertRaises(ValidationError):
            self.lead._check_customer_status_requirements()

    def test_change_status(self):
        """Test lead status changes"""
        self.lead.action_mark_failed()
        self.assertEqual(self.lead.x_status, 'failed')
        self.lead.action_proposal()
        self.assertEqual(self.lead.x_status, 'in progress')
        
    def test_readonly_field_logic(self):
        """Test that readonly fields are computed correctly"""
        self.lead.write({'x_status': 'completed'})
        self.assertTrue(self.lead.x_readonly_fields)
        self.lead.write({'x_status': 'draft'})
        self.assertFalse(self.lead.x_readonly_fields)

    def test_dealer_branch_constraint(self):
        """Ensure dealer branch and state must match"""
        state = self.env['res.country.state'].create({'name': 'Test State', 'code': 'TS'})
        self.dealer_branch.write({'state_id': state.id})
        self.lead.write({'x_state_id': state.id})  # Matching state should pass
        with self.assertRaises(ValidationError):
            self.lead.write({'x_state_id': self.env['res.country.state'].create({'name': 'Another State', 'code': 'AS'}).id})
