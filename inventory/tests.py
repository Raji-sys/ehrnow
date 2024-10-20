from django.test import TestCase
from django.contrib.auth.models import User
from .models import Item, Unit, Department, Record, Purchase
from django.core.exceptions import ValidationError


class ItemModelTest(TestCase):
    def setUp(self):
        # Create necessary objects for testing
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.unit = Unit.objects.create(name='Test Unit')

    def test_total_issued_calculation(self):
        item = Item.objects.create(name='Test Item', unit=self.unit)
        # Create some records
        record1 = Record.objects.create(item=item, quantity=5, issued_by=self.user)
        record2 = Record.objects.create(item=item, quantity=3, issued_by=self.user)

        # Check if the total_issued property is calculated correctly
        self.assertEqual(item.total_issued, record1.quantity + record2.quantity)

    def test_total_store_value_calculation(self):
        # Create multiple items and purchases
        item1 = Item.objects.create(name='Item1', unit=self.unit, unit_price=5.0, total_purchased_quantity=10)
        item2 = Item.objects.create(name='Item2', unit=self.unit, unit_price=8.0, total_purchased_quantity=15)
        Purchase.objects.create(item=item1, quantity_purchased=10)
        Purchase.objects.create(item=item2, quantity_purchased=15)

        # Check if the total_store_value class method works
        self.assertEqual(Item.total_store_value(), item1.total_value + item2.total_value)

    def test_balance_calculation(self):
        item = Item.objects.create(name='Test Item', unit=self.unit, total_purchased_quantity=10)
        record = Record.objects.create(item=item, quantity=5, issued_by=self.user)

        # Check if the balance property is calculated correctly
        self.assertEqual(record.balance, item.total_purchased_quantity - record.quantity)

        # Add another record
        record2 = Record.objects.create(item=item, quantity=3, issued_by=self.user)

        # Check if the balance is updated correctly
        self.assertEqual(record2.balance, record.balance - record2.quantity)

        # Test that the balance is 0 when the quantity matches the total purchased
        record3 = Record.objects.create(item=item, quantity=item.total_purchased_quantity, issued_by=self.user)
        self.assertEqual(record3.balance, 0)


class RecordModelTest(TestCase):
    def setUp(self):
        # Create necessary objects for testing
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.unit = Unit.objects.create(name='Test Unit')

    def test_create_record(self):
        item = Item.objects.create(name='Test Item', unit=self.unit, total_purchased_quantity=10)

        # Create a record
        record = Record.objects.create(item=item, quantity=5, issued_by=self.user)

        # Check that the record was created successfully
        self.assertEqual(Record.objects.count(), 1)

        # Check that the balance is updated correctly
        self.assertEqual(record.balance, item.total_purchased_quantity - record.quantity)

        # Check that the associated Item model is updated
        item.refresh_from_db()
        self.assertEqual(item.total_issued, record.quantity)

    def test_create_record_with_zero_quantity(self):
        item = Item.objects.create(name='Test Item', unit=self.unit, total_purchased_quantity=10)

        # Create a record with zero quantity (allowed during testing)
        record = Record.objects.create(item=item, quantity=0, issued_by=self.user)

        # Check that the record was created successfully
        self.assertEqual(Record.objects.count(), 1)

        # Check that the balance is updated correctly
        self.assertEqual(record.balance, item.total_purchased_quantity)

        # Check that the associated Item model is updated
        item.refresh_from_db()
        self.assertEqual(item.total_issued, record.quantity)

    # def test_create_record_with_negative_quantity(self):
    #     item = Item.objects.create(name='Test Item', unit=self.unit, total_purchased_quantity=10)
    #     with self.settings(DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3'}}):
    #         record=Record(item=item,quantity= -3)
    #         try:
    #             record.save()
    #             self.fail("ValidationEroor not raised for negative quanity")
    #         except ValidationError as e:
    #         # Check the specific error message if needed
    #             self.assertIn('Quantity cannot be negative.', str(e))

    #     # Check that no record was created
    #         self.assertEqual(Record.objects.count(), 0)



class PurchaseModelTest(TestCase):
    def setUp(self):
        # Create necessary objects for testing
        self.unit = Unit.objects.create(name='Test Unit')

    def test_create_purchase(self):
        item = Item.objects.create(name='Test Item', unit=self.unit)

        # Create a purchase
        purchase = Purchase.objects.create(item=item, quantity_purchased=10)

        # Check that the purchase was created successfully
        self.assertEqual(Purchase.objects.count(), 1)

        # Check that the associated Item model is updated
        item.refresh_from_db()
        self.assertEqual(item.total_purchased_quantity, purchase.quantity_purchased)

    def test_create_purchase_with_zero_quantity(self):
        item = Item.objects.create(name='Test Item', unit=self.unit)

        # Create a purchase with zero quantity
        purchase = Purchase.objects.create(item=item, quantity_purchased=0)

        # Check that the purchase was created successfully
        self.assertEqual(Purchase.objects.count(), 1)

        # Check that the associated Item model is updated
        item.refresh_from_db()
        self.assertEqual(item.total_purchased_quantity, purchase.quantity_purchased)

    # def test_create_purchase_with_negative_quantity(self):
    #     item = Item.objects.create(name='Test Item', unit=self.unit)

    #     # Attempt to create a purchase with negative quantity (should raise ValidationError)
    #     with self.assertRaises(ValidationError):
    #         Purchase.objects.create(item=item, quantity_purchased=-3)

    #     # Check that no purchase was created
    #     self.assertEqual(Purchase.objects.count(), 0)

    # Add more test cases as needed
