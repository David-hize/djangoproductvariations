from django.urls import path
from core.views import (
	HomeView,
	ItemDetailView,
	OrderSummaryView,
	CheckoutView,
	add_to_cart,
	remove_from_cart,
	remove_single_item_from_cart
)

app_name = 'core'

urlpatterns = [
	path('', HomeView.as_view(), name='homepage'),
	path('checkout/', CheckoutView.as_view(), name='checkout'),
	path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
	path('product/<slug>/', ItemDetailView.as_view(), name='product'),
	path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
	path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
	path('remove-item-cart/<slug>/', remove_single_item_from_cart, name='remove-single-item-from-cart'),

]