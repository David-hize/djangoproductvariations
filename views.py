from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, reverse, render_to_response, get_object_or_404
from django.views.generic import ListView, DetailView, View
from core.models import  Item, OrderItem, Order, Variation, BillingAddress
from django.utils import timezone
from core.forms import CheckoutForm


class HomeView(ListView):
	model = Item
	paginate_by = 10
	template_name = "homepage.html"

class OrderSummaryView(LoginRequiredMixin, View):
	def get(self, *args, **kwargs):

		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			context = {
				'object': order
			}
			return render(self.request, "order_summary.html", context)
		except ObjectDoesNotExist:
			messages.error(self.request, "You do not have an active order")
			return redirect("/")

class ItemDetailView(DetailView):
	model = Item
	template_name = "product.html"


class CheckoutView(View):
	def get(self, *args, **kwargs):
		form = CheckoutForm()
		# order
		order = Order.objects.get(user=self.request.user, ordered=False)
		context = {
			'form': form,
			'order': order
		}
		return render(self.request, "checkout.html", context)

	def post(self, *args, **kwargs):
		form = CheckoutForm(self.request.POST or None)
		print(self.request.POST)
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			if form.is_valid():
				street_address = form.cleaned_data.get('street_address')
				apartment_address = form.cleaned_data.get('apartment_address')
				country = form.cleaned_data.get('country')
				state = form.cleaned_data.get('state')
				city = form.cleaned_data.get('city')
				phone = form.cleaned_data.get('phone')
				# TODO: add functionality for these fields
				# same_shipping_address = form.cleaned_data.get('same_shipping_address')
				# save_info = form.cleaned_data.get('save_info')
				payment_option = form.cleaned_data.get('payment_option')
				billing_address = BillingAddress(
					user=self.request.user,
					street_address=street_address,
					apartment_address=apartment_address,
					country=country,
					state=state,
					city=city,
					phone=phone,
				)
				billing_address.save()
				order.billing_address = billing_address
				order.save()
				# TODO: add redirect to the selected payment option
				return redirect("core:checkout")
			messages.warning(self.request, "Failed checkout")
			return redirect("core:checkout")
		except ObjectDoesNotExist:
			messages.error(self.request, "You do not have an active order")
			return redirect("core:order-summary")


@login_required
def add_to_cart(request,slug):
	item = get_object_or_404(Item, slug=slug)

	order_item_qs = OrderItem.objects.filter(
		item=item,
		user=request.user,
		ordered=False
	)
	
	item_var = [] #item variation
	if request.method == 'POST':
		for items in request.POST:
			key = items
			val = request.POST[key]
			try:
				v = Variation.objects.get(
					item=item,
					category__iexact=key,
					title__iexact=val
				)
				item_var.append(v)
			except:
				pass

		if len(item_var) > 0:
			for items in item_var:
				order_item_qs = order_item_qs.filter(
					variation__exact=items,
				)
					
    
	if order_item_qs.exists():
		order_item = order_item_qs.first()
		# for order_item in order_item_qs:
		 # order_item = order_item_qs.first()
		order_item.quantity += 1
		order_item.save()
		#print(order_item_qs)

	else:
		order_item = OrderItem.objects.create(
			item=item,
			user=request.user,
			ordered=False
		)
		order_item.variation.add(*item_var)
		order_item.save()

	
	order_qs = Order.objects.filter(user=request.user, ordered=False)
	if order_qs.exists():
		order = order_qs[0]
		#check if the order item is in the order
		if not order.items.filter(item__id=order_item.id).exists():
			order.items.add(order_item)
			messages.info(request, "This item quantity was updated.")
			return redirect("core:order-summary")
	else:
		ordered_date = timezone.now()
		order = Order.objects.create(user=request.user, ordered_date=ordered_date)
		order.items.add(order_item)
		messages.info(request, "This item was added to cart.")
		return redirect("core:order-summary")


@login_required	
def remove_from_cart(request, slug):
	item = get_object_or_404(Item,slug=slug)
	order_qs = Order.objects.filter(
		user=request.user, 
		ordered=False
	)
	if order_qs.exists():
		order = order_qs[0]
		#check if the order item is in the order
		if order.items.filter(item__slug=item.slug).exists():
			order_item = OrderItem.objects.filter(
				item=item,
				user=request.user,
				ordered=False
			)[0]
			order.items.remove(order_item)
			messages.info(request, "This item was removed from cart.")
			return redirect("core:order-summary") #core:order-summary
		else:
			messages.info(request, "This item was not in your cart.")
			return redirect("core:order-summary")
	else:
		messages.info(request, "You do not have an active order.")
		return redirect("core:order-summary")

@login_required	
def remove_single_item_from_cart(request, slug):
	item = get_object_or_404(Item,slug=slug)
	order_qs = Order.objects.filter(
		user=request.user, 
		ordered=False
	)
	if order_qs.exists():
		order = order_qs[0]
		#check if the order item is in the order
		if order.items.filter(item__slug=item.slug).exists():
			order_item = OrderItem.objects.filter(
				item=item,
				user=request.user,
				ordered=False
			)[0]
			if order_item.quantity > 1:
				order_item.quantity -= 1
				order_item.save()
			else:
				order.items.remove(order_item)
			messages.info(request, "This item quantity was updated.")
			return redirect("core:order-summary")
		else:
			messages.info(request, "This item was not in your cart.")
			return redirect("core:product", slug=slug)
	else:
		messages.info(request, "You do not have an active order.")
		return redirect("core:product", slug=slug)
	