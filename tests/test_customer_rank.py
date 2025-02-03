# my_module/tests/test_customer_rank.py

from odoo.tests.common import TransactionCase


class TestCustomerRank(TransactionCase):

    def setUp(self):
        """Set up test data."""
        super(TestCustomerRank, self).setUp()
        # Creating a test customer rank record
        self.customer_rank = self.env['customer.rank'].create({
            'rank_name': 'Gold',
            'min_hino_vehicles': 5,
            'max_hino_vehicles': 10,
            'min_owned_vehicles': 5,
            'max_owned_vehicles': 10,
        })

    def test_customer_rank_creation(self):
        """Test the creation of a customer rank."""
        self.assertEqual(self.customer_rank.rank_name, 'Gold')
        self.assertEqual(self.customer_rank.min_hino_vehicles, 5)

    def test_customer_rank_update(self):
        """Test updating a customer rank."""
        # Update the rank name
        self.customer_rank.write({'rank_name': 'Platinum'})
        self.assertEqual(self.customer_rank.rank_name, 'Platinum')

    def test_customer_rank_constraints(self):
        """Test any constraints or logic on the model."""
        with self.assertRaises(Exception):
            # Try creating a rank with invalid data (e.g., max_hino_vehicles < min_hino_vehicles)
            self.env['customer.rank'].create({
                'rank_name': 'Silver',
                'min_hino_vehicles': 10,
                'max_hino_vehicles': 5,
            })

    def test_customer_hino_min_max_overlap(self):
        """Test any constraints or logic on the model."""
        with self.assertRaises(Exception):
            # Try creating a rank with invalid data (e.g., max_hino_vehicles < min_hino_vehicles)
            self.env['customer.rank'].create({
                'rank_name': 'Silver',
                'min_hino_vehicles': 8,
                'max_hino_vehicles': 12,
            })
    def test_customer_owned_min_max_overlap(self):
        """Test any constraints or logic on the model."""
        with self.assertRaises(Exception):
            # Try creating a rank with invalid data (e.g., max_hino_vehicles < min_hino_vehicles)
            self.env['customer.rank'].create({
                'rank_name': 'Silver',
                'min_owned_vehicles': 8,
                'max_owned_vehicles': 12,
            })