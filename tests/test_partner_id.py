from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestCustomLead(TransactionCase):

    def setUp(self):
        super(TestCustomLead, self).setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Công ty ABC',
            'vat_number': '123456789',
            'identity_number': '1234567890123'
        })

        self.lead = self.env['crm.lead'].create({
            'name': 'Khách hàng tiềm năng',
            'x_phone': '0123456789',
            'x_email_from': 'test@example.com',
            'partner_id': self.partner.id
        })

    def test_create_lead(self):
        self.assertTrue(self.lead, "Lead không được tạo thành công")

    def test_onchange_partner_id(self):
        self.lead._onchange_partner_id()
        self.assertEqual(self.lead.x_vat, self.partner.vat_number, "Số ĐKKD không tự động cập nhật")
        self.assertEqual(self.lead.x_identity_number, self.partner.identity_number, "Số CCCD không tự động cập nhật")

    def test_invalid_identity_number(self):
        self.lead.x_identity_number = '1234'
        with self.assertRaises(ValidationError):
            self.lead._check_identity_number()
        
        self.lead.x_identity_number = '123456789012345'
        with self.assertRaises(ValidationError):
            self.lead._check_identity_number()

        self.lead.x_identity_number = 'abc1234567'
        with self.assertRaises(ValidationError):
            self.lead._check_identity_number()

    def test_valid_identity_number(self):
        """Kiểm tra số CCCD hợp lệ"""
        self.lead.x_identity_number = '123456789'
        self.lead._check_identity_number() 

        self.lead.x_identity_number = '1234567890123'
        self.lead._check_identity_number()
