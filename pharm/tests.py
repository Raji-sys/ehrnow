from django.core.exceptions import ValidationError
from .models import *
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

# class ItemModelTest(TestCase):
#     def setUp(self):
#         self.category = Category.objects.create(name="Test Category")
#         self.user = User.objects.create(username="testuser")
#         self.item = Item.objects.create(
#             name="Test Item",
#             added_by=self.user,
#             category=self.category,
#             unit_price=10.0,
#             expiration_date="2023-12-31",
#             total_purchased_quantity=100,
#         )

#     def test_total_value(self):
#         self.assertEqual(self.item.total_value, 1000.0)

#     def test_total_store_value(self):
#         total_value = Item.total_store_value()
#         self.assertEqual(total_value, 1000.0)

#     # Add more tests for other methods and properties in the Item model

# class RecordModelTest(TestCase):
#     def setUp(self):
#         self.category = Category.objects.create(name="Test Category")
#         self.user = User.objects.create(username="testuser")
#         self.item = Item.objects.create(
#             name="Test Item",
#             added_by=self.user,
#             category=self.category,
#             unit_price=10.0,
#             expiration_date="2023-12-31",
#             total_purchased_quantity=100,
#         )
#         self.record = Record.objects.create(
#             category=self.category,
#             item=self.item,
#             unit_issued_to=Unit.ACCIDENT_AND_EMERGENCY,
#             quantity=10,
#             issued_by=self.user,
#         )

#     def test_save_method(self):
#         self.assertEqual(self.record.quantity, 10)
#         self.assertEqual(self.record.balance, 90)

#     # Add more tests for other methods and properties in the Record model

# class PurchaseModelTest(TestCase):
#     def setUp(self):
#         self.category = Category.objects.create(name="Test Category")
#         self.user = User.objects.create(username="testuser")
#         self.item = Item.objects.create(
#             name="Test Item",
#             added_by=self.user,
#             category=self.category,
#             unit_price=10.0,
#             expiration_date="2023-12-31",
#             total_purchased_quantity=100,
#         )
#         self.purchase = Purchase.objects.create(
#             item=self.item,
#             quantity_purchased=20,
#             expiration_date="2023-12-31",
#         )

#     def test_save_method(self):
#         self.assertEqual(self.item.total_purchased_quantity, 120)

#     # Add more tests for other methods and properties in the Purchase model

# class MoreRecordModelTest(TestCase):
#     def setUp(self):
#         self.category = Category.objects.create(name="Test Category")
#         self.user = User.objects.create(username="testuser")
#         self.item = Item.objects.create(
#             name="Test Item",
#             added_by=self.user,
#             category=self.category,
#             unit_price=10.0,
#             expiration_date="2023-12-31",
#             total_purchased_quantity=100,
#         )
#         self.record = Record.objects.create(
#             category=self.category,
#             item=self.item,
#             unit_issued_to=Unit.ACCIDENT_AND_EMERGENCY,
#             quantity=10,
#             issued_by=self.user,
#         )

#         try:
#             record = Record.objects.create(
#                 category=self.category,
#                 item=self.item,
#                 unit_issued_to=Unit.ACCIDENT_AND_EMERGENCY,
#                 quantity=110,  # attempting to issue more than available
#                 issued_by=self.user,
#             )
#         except Exception as e:
#             print(f"Caught exception: {type(e).__name__}, {e}")
#             raise e  # 
#     # Add more tests for other methods and properties in the Record model

# class MorePurchaseModelTest(TestCase):
#     def setUp(self):
#         self.category = Category.objects.create(name="Test Category")
#         self.user = User.objects.create(username="testuser")
#         self.item = Item.objects.create(
#             name="Test Item",
#             added_by=self.user,
#             category=self.category,
#             unit_price=10.0,
#             expiration_date="2023-12-31",
#             total_purchased_quantity=100,
#         )
#         self.purchase = Purchase.objects.create(
#             item=self.item,
#             quantity_purchased=20,
#             expiration_date="2023-12-31",
#         )

#     def test_save_method(self):
#         # Test normal save behavior
#         self.assertEqual(self.item.total_purchased_quantity, 120)

#         # Test purchasing a negative quantity
#         try:
#             purchase = Purchase.objects.create(
#                 item=self.item,
#                 quantity_purchased=5,  # non-negative value
#                 expiration_date="2023-12-31",
#             )
#         except Exception as e:
#             print(f"Caught exception: {type(e).__name__}, {e}")
#             raise e  # re-raise the e

#     # Add more tests for other methods and properties in the Purchase model

# class StoreViewsTest(TestCase):
#     def setUp(self):
#         # Create a test user
#         self.user = User.objects.create_user(username='testuser', password='testpassword')

#         # Create a test category
#         self.category = Category.objects.create(name="Test Category")

#         # Create a test item
#         self.item = Item.objects.create(
#             name="Test Item",
#             added_by=self.user,
#             category=self.category,
#             unit_price=10.0,
#             expiration_date="2023-12-31",
#             total_purchased_quantity=100,)

#     def test_custom_login_view(self):
#         response = self.client.get(reverse('signin'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'login.html')

#     def test_index_view(self):
#         # Log in the user
#         self.client.force_login(self.user)

#         response = self.client.get(reverse('index'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'store/index.html')

#     def test_items_list_view(self):
#         # Log in the user
#         self.client.force_login(self.user)

#         response = self.client.get(reverse('list'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'store/items_list.html')

#     # Add similar tests for other views

#     def test_create_item_view(self):
#     # Log in the user
#         self.client.force_login(self.user)

#         response = self.client.get(reverse('create_item'))
#         self.assertEqual(response.status_code, 200)  # Initial rendering of the form
#         self.assertTemplateUsed(response, 'store/create_item.html')

#         # Test form submission and follow redirects
#         data = {
#             'name': 'Test Item',
#             'added_by': self.user.id,
#             'category': 'Test Category',
#             'unit_price': 10.0,
#             'expiration_date': '2023-12-31',
#             'total_purchased_quantity': 100,
#         }
#         response = self.client.post(reverse('create_item'), data, follow=True)
        
#         # Check the status code after form submission, should be 200 after following the redirect
#         self.assertEqual(response.status_code, 200)

#         # Check if the item was created
#         self.assertEqual(Item.objects.count(), 1)

#     # Add more assertions based on the expected behavior of the redirected view



#     def test_record_pdf_view(self):
#         # Log in the user
#         self.client.force_login(self.user)

#         # Create some records
#         record = Record.objects.create(
#             category=self.category,
#             item=self.item,
#             unit_issued_to='ACCIDENT AND EMERGENCY',
#             quantity=10,
#             issued_by=self.user,
#         )

#         response = self.client.get(reverse('record_pdf'))
#         self.assertEqual(response.status_code, 200)
        # Add more assertions based on the expected behavior of the view


# class MoreStoreViewsTest(TestCase):
#     def setUp(self):
#         # Create a test user
#         self.user = User.objects.create_user(username='testuser', password='testpassword')
#         self.superuser = User.objects.create_superuser(username='superuser', password='superpassword')
#         # Create a test category
#         self.category = Category.objects.create(name="Test Category")

#         # Create a test item
#         self.item = Item.objects.create(
#             name="Test Item",
#             added_by=self.user,
#             category=self.category,
#             unit_price=10.0,
#             expiration_date="2023-12-31",
#             total_purchased_quantity=100,
#         )

    # def test_create_record_view(self):
    #     # Log in the user
    #     self.client.force_login(self.user)

    #     response = self.client.get(reverse('create_record'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'store/create_record.html')

    #     # Test form submission
    #     data = {
    #         'category': self.category.id,
    #         'item': self.item.id,
    #         'unit_issued_to': 'ACCIDENT AND EMERGENCY',
    #         'quantity': 10,
    #     }
    #     response = self.client.post(reverse('create_record'), data)
    #     self.assertEqual(response.status_code, 302)  # Redirect status code
    #     self.assertEqual(Record.objects.count(), 1)  # Check if the record was created

    # def test_reports_view(self):
    #     # Log in the user
    #     self.client.force_login(self.user)

    #     response = self.client.get(reverse('report'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'store/report.html')

    # def test_item_report_view(self):
    #     # Log in the user
    #     self.client.force_login(self.user)

    #     response = self.client.get(reverse('item_report'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'store/item_report.html')

    # def test_record_report_view(self):
    #     # Log in the user
    #     self.client.force_login(self.user)

    #     response = self.client.get(reverse('record_report'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'store/record_report.html')


    # def test_worth_view(self):
    #     # Log in the superuser
    #     self.client.force_login(self.superuser)

    #     response = self.client.get(reverse('worth'))

    #     # Check if the response is a success (status code 200)
    #     self.assertEqual(response.status_code, 200)

    #     # Check if the correct template is used
    #     self.assertTemplateUsed(response, 'store/worth.html')


class DynamicDropdownTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # Create test categories
        self.category1 = Category.objects.create(name="Category 1")
        self.category2 = Category.objects.create(name="Category 2")

        # Create test items
        self.item1 = Drug.objects.create(name="Item 1", category=self.category1)
        self.item2 = Drug.objects.create(name="Item 2", category=self.category1)
        self.item3 = Drug.objects.create(name="Item 3", category=self.category2)

    def test_dynamic_dropdown(self):
        # Log in the user
        self.client.force_login(self.user)

        # Access the view that contains the form
        response = self.client.get(reverse('pharm:get_drugs_for_category', kwargs={'category_id': self.category1.id}))

        # Check that the response is successful (status code 200)
        self.assertEqual(response.status_code, 200)

        # Fetch all categories from the database
        categories = Category.objects.all()

        # Iterate over categories and simulate category change events
        for category in categories:
            response = self.client.get(reverse('get_items_for_category', kwargs={'category_id': category.id}))

            # Check that the response is successful (status code 200)
            self.assertEqual(response.status_code, 200)

            # Check that the items returned match the items associated with the current category
            data = response.json()
            if category == self.category1:
                self.assertEqual(len(data), 2)  # Expecting two items for Category 1
                self.assertEqual(data[0]['id'], self.item1.id)
                self.assertEqual(data[1]['id'], self.item2.id)
            elif category == self.category2:
                self.assertEqual(len(data), 1)  # Expecting one item for Category 2
                self.assertEqual(data[0]['id'], self.item3.id)

