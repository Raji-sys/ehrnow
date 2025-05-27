# urls.py
from django.urls import path
from . import views 
from .views import *

app_name = 'erp'

urlpatterns = [

    path('account/expenses/', ExpenseListView.as_view(), name='expenses_list'),
    path('account/expense/autocomplete/', views.expense_autocomplete, name='expense_autocomplete'),
    path('account/expenses/create/', ExpenseCreateView.as_view(), name='expense_create'),
    path('account/expenses/<int:pk>/update/', ExpenseUpdateView.as_view(), name='expense_update'),  

    path('account/company-account/', CompanyAccountListView.as_view(), name='company_account_list'),
    path('company_account/autocomplete/', views.company_account_autocomplete, name='company_account_autocomplete'),
    path('account/company-account/create/', CompanyAccountCreateView.as_view(), name='company_account_create'),
    path('account/company-account/<int:pk>/update/', CompanyAccountUpdateView.as_view(), name='company_account_update'),  
    path('account/accounts/<int:pk>/fund/', FundAccountView.as_view(), name='fund_account'),
    path('account/accounts/<int:pk>/deduct/', DeductAccountView.as_view(), name='deduct_account'),
    path('account/accounts/transfer/', AccountTransferView.as_view(), name='account_transfer'),
    path('account/accounts/transactions/', TransactionListView.as_view(), name='transaction_list'),

    path('under-construction/', UnderConstructionView.as_view(), name='under_construction'),
    path('account-index/', AccountingIndexView.as_view(), name='accounting_index'),
]
