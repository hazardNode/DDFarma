# core/views.py
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import resolve, reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from allauth.account.views import ConfirmEmailView, PasswordResetView, PasswordResetFromKeyView
from django.contrib import messages
from .cart import Cart
from django.views.generic.edit import FormView
from core.models import Product, Order, Category, User, ProductImage, PaymentMethod, Address, ShippingMethod, OrderItem
from core.forms import ProductForm, CategoryForm, UserForm, UserProfileForm, ProductImageForm, MultipleImageUploadForm, CustomResetPasswordKeyForm
from django import forms
from .stripe_utils import create_payment_method, delete_payment_method, set_default_payment_method, create_stripe_customer
import json
import stripe
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import transaction
from django.urls import reverse
from decimal import Decimal
from allauth.account.utils import url_str_to_user_pk
from allauth.account.utils import user_pk_to_url_str
from django.contrib.auth import get_user_model
from allauth.account.forms import default_token_generator

def product_list(request):
    products = Product.objects.all()
    return render(request, 'core/management/product_list.html', {'products': products})


def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        image_form = MultipleImageUploadForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save()

            # Check if there are images to upload
            if 'images' in request.FILES and any(request.FILES.getlist('images')):
                if image_form.is_valid():
                    files = request.FILES.getlist('images')
                    set_first_as_primary = image_form.cleaned_data.get('set_primary',
                                                                       True)  # Default to True for new products

                    for i, img in enumerate(files):
                        # Make the first image primary if requested or if it's the only image
                        is_primary = (i == 0 and (set_first_as_primary or len(files) == 1))
                        ProductImage.objects.create(
                            product=product,
                            image=img,
                            is_primary=is_primary
                        )

                    messages.success(request, 'Product created successfully with images.')
                else:
                    messages.warning(request, 'Product created but there was an issue with the image upload.')
            else:
                messages.success(request, 'Product created successfully.')

            return redirect('product_list')
    else:
        form = ProductForm()
        image_form = MultipleImageUploadForm()

    return render(request, 'core/management/form.html', {
        'form': form,
        'image_form': image_form,
        'title': 'Create New Product',
        'is_create': True,  # Flag to indicate this is a create form
        'is_product_form': True
    })


def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        image_form = MultipleImageUploadForm(request.POST, request.FILES)

        # Check form validity first
        if form.is_valid():
            form.save()

            # Check if there are images to upload
            if 'images' in request.FILES and any(request.FILES.getlist('images')):
                if image_form.is_valid():
                    files = request.FILES.getlist('images')
                    set_first_as_primary = image_form.cleaned_data.get('set_primary', False)

                    for i, img in enumerate(files):
                        # Make the first uploaded image primary if set_primary is checked
                        is_primary = (i == 0 and set_first_as_primary)
                        ProductImage.objects.create(
                            product=product,
                            image=img,
                            is_primary=is_primary
                        )

                    messages.success(request, 'Product and images updated successfully.')
                else:
                    messages.warning(request, 'Product updated but there was an issue with the image upload.')
            else:
                messages.success(request, 'Product updated successfully.')

            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
        image_form = MultipleImageUploadForm()

    return render(request, 'core/management/form.html', {
        'form': form,
        'object': product,
        'title': f'Edit {product.name}',
        'image_form': image_form,
        'images': product.images.all(),
        'is_create': False,
        'is_product_form': True
    })

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'core/management/product_confirm_delete.html', {'object': product})


def set_primary_image(request, pk, image_id):
    product = get_object_or_404(Product, pk=pk)
    image = get_object_or_404(ProductImage, id=image_id, product=product)

    # Set as primary
    image.is_primary = True
    image.save()

    messages.success(request, 'Primary image updated.')
    return redirect('product_update', pk=pk)


def delete_image(request, pk, image_id):
    product = get_object_or_404(Product, pk=pk)
    image = get_object_or_404(ProductImage, id=image_id, product=product)

    image.delete()
    messages.success(request, 'Image deleted.')
    return redirect('product_update', pk=pk)
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'core/management/category_list.html', {'categories': categories})

def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'core/management/form.html', {
        'form': form,
        'is_create': False,
    })

def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'core/management/form.html', {
        'form': form,
        'is_create': False,
    })

def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'core/management/category_confirm_delete.html', {'object': category})

def user_list(request):
    users = User.objects.all()
    return render(request, 'core/management/user_list.html', {'users': users})

def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserForm(instance=user)
    return render(request, 'core/management/form.html', {
        'form': form,
        'is_create': False,
    })

def management_dashboard(request):
    # Get the current URL name
    current_url_name = resolve(request.path_info).url_name

    # Define active states for sidebar links
    active_states = {
        'dashboard': current_url_name == 'management_dashboard',
        'products': current_url_name in ['product_list', 'product_create', 'product_update', 'product_delete'],
        'categories': current_url_name in ['category_list', 'category_create', 'category_update', 'category_delete'],
        'orders': current_url_name in ['order_list', 'order_detail'],
        'users': current_url_name in ['user_list', 'user_update'],
    }

    context = {
        'active_states': active_states,
    }
    return render(request, 'core/management/dashboard.html', context)


def order_list(request):
    # Fetch all orders ordered by the most recent order date
    orders = Order.objects.all().order_by('-order_date')

    # Pass the orders to the template
    return render(request, 'core/management/order_list.html', {'orders': orders})


def order_detail(request, pk):
    # Fetch the specific order or return a 404 error if not found
    order = get_object_or_404(Order, pk=pk)

    # Pass the order and its related items to the template
    return render(request, 'core/management/order_detail.html', {'order': order})

def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'core/order_history.html', {'orders': orders})

def landing_page(request):
    return render(request, 'core/landing_page.html')


def shop(request):
    categories = Category.objects.all()

    # Organize products by category
    context = {
        'categories': categories,
    }
    return render(request, 'core/shop.html', context)


def product_detail(request, product_id):
    # Get the product or return 404 if not found
    product = get_object_or_404(Product, id=product_id)

    # Get related products from the same category, excluding the current product
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]  # Limit to 4 related products

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'product_detail.html', context)


def cart_detail(request):
    cart = Cart(request)

    # Load products with their images
    product_ids = [int(id) for id in cart.cart.keys()]

    # Ensure products are loaded with their images for the template
    from .models import Product
    products = Product.objects.filter(id__in=product_ids).prefetch_related('images')

    # Create a dictionary to quickly look up products
    product_dict = {str(p.id): p for p in products}

    # Replace product objects in cart items
    for item in cart:
        product_id = str(item['product'].id)
        if product_id in product_dict:
            item['product'] = product_dict[product_id]

    context = {
        'cart': cart
    }
    return render(request, 'cart.html', context)

@require_POST
def cart_update_ajax(request):
    cart = Cart(request)
    data = json.loads(request.body)

    product_id = data.get('product_id')
    action = data.get('action')
    quantity = int(data.get('quantity', 1))

    product = get_object_or_404(Product.objects.prefetch_related('images'), id=product_id)

    if action == 'add':
        cart.add(product=product, quantity=quantity, override_quantity=False)
    elif action == 'update':
        cart.add(product=product, quantity=quantity, override_quantity=True)
    elif action == 'remove':
        cart.remove(product)

    cart_data = cart.get_cart_data()
    return JsonResponse({'success': True, 'cart': cart_data})


def get_cart_count(request):
    cart = Cart(request)
    return render(request, 'partials/cart_icon.html', {'cart': cart})


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, f'{product.name} removed from your cart')
    return redirect('cart_detail')


@login_required
def account_dashboard(request):
    return render(request, 'account/account_dashboard.html')


@login_required
def update_profile(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        # Update the user's information
        user = request.user
        user.first_name = first_name
        user.last_name = last_name

        try:
            user.save()
            return JsonResponse({
                'success': True,
                'message': 'Profile updated successfully!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating profile: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

@login_required
def email_management(request):
    """View for managing user email addresses."""
    if request.method == 'POST':
        # Handle adding a new email
        if 'action_add' in request.POST:
            email = request.POST.get('email')
            if email:
                if EmailAddress.objects.filter(email=email).exists():
                    messages.error(request, 'This email is already in use.')
                else:
                    email_address = EmailAddress.objects.add_email(
                        request, request.user, email, confirm=True)
                    messages.success(request,
                                     f'Verification email sent to {email}.')
                    return redirect('account_email_verification_sent')

        # Handle setting an email as primary
        elif 'action_primary' in request.POST:
            email = request.POST.get('email')
            emailaddress = EmailAddress.objects.get(
                user=request.user, email=email)
            if not emailaddress.verified:
                messages.error(request,
                               'You cannot set an unverified email as primary.')
            else:
                emailaddress.set_as_primary()
                messages.success(request,
                                 f'{email} is now your primary email address.')

        # Handle resending verification email
        elif 'action_send' in request.POST:
            email = request.POST.get('email')
            try:
                email_address = EmailAddress.objects.get(
                    user=request.user, email=email)
                email_address.send_confirmation(request)
                messages.success(request,
                                 f'Verification email resent to {email}.')
                return redirect('account_email_verification_sent')
            except EmailAddress.DoesNotExist:
                messages.error(request, 'Email address not found.')

        # Handle removing an email
        elif 'action_remove' in request.POST:
            email = request.POST.get('email')
            try:
                email_address = EmailAddress.objects.get(
                    user=request.user, email=email)

                # Check if it's the primary email
                if email_address.primary:
                    if EmailAddress.objects.filter(user=request.user).count() > 1:
                        messages.error(request,
                                       'Cannot remove primary email. Set another email as primary first.')
                        return redirect('account_email')
                    else:
                        messages.error(request,
                                       'Cannot remove your only email address.')
                        return redirect('account_email')

                # Remove the email
                email_address.delete()
                messages.success(request, f'{email} has been removed.')
            except EmailAddress.DoesNotExist:
                messages.error(request, 'Email address not found.')

    # Get all email addresses for the user
    emails = EmailAddress.objects.filter(user=request.user)

    return render(request, 'core/account/email.html', {'emails': emails})


@login_required
def email_verification_sent(request):
    """View shown after a verification email has been sent."""
    return render(request, 'core/account/email_verification_sent.html')


def verify_email(request, uidb64, token):
    """View to verify an email address from the link in the email."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        email_address = EmailAddress.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, EmailAddress.DoesNotExist):
        email_address = None

    if email_address is not None and account_activation_token.check_token(email_address, token):
        email_address.verified = True
        email_address.save()

        # If this is the user's only email, make it primary
        if not EmailAddress.objects.filter(user=email_address.user, primary=True).exists():
            email_address.set_as_primary()

        context = {
            'success': True,
            'email': email_address.email
        }
        messages.success(request, f'Your email {email_address.email} has been verified!')
    else:
        context = {
            'success': False,
            'email': request.user.email if request.user.is_authenticated else ''
        }

    return render(request, 'core/account/email_verification.html', context)


class CustomConfirmEmailView(ConfirmEmailView):
    """
    Custom view to handle email confirmation and redirect appropriately
    """

    def get(self, *args, **kwargs):
        try:
            self.object = self.get_object()
            if self.object.email_address.verified:
                messages.info(self.request, "This email has already been verified.")
                return redirect("/")
        except Exception:
            messages.error(
                self.request,
                "This email confirmation link has expired or is invalid. Please request a new confirmation email."
            )
            return redirect("landing_page")

        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """
        Handle the POST request after confirmation
        """
        # Let the parent class handle the actual confirmation
        response = super().post(*args, **kwargs)

        # Always redirect to home with a message
        messages.success(
            self.request,
            "Your email address has been confirmed successfully."
        )
        return redirect("landing_page")


@login_required
def address_management(request):
    """View for managing user shipping addresses."""
    # Get all addresses for the current user
    addresses = Address.objects.filter(user=request.user)

    return render(request, 'account/address_management.html', {
        'addresses': addresses
    })


@login_required
def address_create(request):
    """Create a new address."""
    if request.method == 'POST':
        street = request.POST.get('street')
        city = request.POST.get('city')
        province = request.POST.get('province')
        postal_code = request.POST.get('postal_code')
        phone = request.POST.get('phone', '')
        is_default = request.POST.get('is_default') == 'on'

        try:
            address = Address(
                user=request.user,
                street=street,
                city=city,
                province=province,
                postal_code=postal_code,
                phone=phone,
                is_default=is_default
            )
            address.save()

            return JsonResponse({
                'success': True,
                'message': 'Address added successfully!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error adding address: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })


@login_required
def address_detail(request, address_id):
    """Get address details."""
    try:
        address = Address.objects.get(id=address_id, user=request.user)

        return JsonResponse({
            'success': True,
            'address': {
                'id': address.id,
                'street': address.street,
                'city': address.city,
                'province': address.province,
                'postal_code': address.postal_code,
                'phone': address.phone,
                'is_default': address.is_default
            }
        })
    except Address.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Address not found'
        })


@login_required
def address_update(request, address_id):
    """Update an existing address."""
    try:
        address = Address.objects.get(id=address_id, user=request.user)

        if request.method == 'POST':
            address.street = request.POST.get('street')
            address.city = request.POST.get('city')
            address.province = request.POST.get('province')
            address.postal_code = request.POST.get('postal_code')
            address.phone = request.POST.get('phone', '')
            address.is_default = request.POST.get('is_default') == 'on'

            address.save()

            return JsonResponse({
                'success': True,
                'message': 'Address updated successfully!'
            })

        return JsonResponse({
            'success': False,
            'message': 'Invalid request method'
        })
    except Address.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Address not found'
        })


@login_required
def address_delete(request, address_id):
    """Delete an address."""
    try:
        address = Address.objects.get(id=address_id, user=request.user)

        if request.method == 'POST':
            # Don't allow deleting the default address if it's the only one
            if address.is_default and Address.objects.filter(user=request.user).count() <= 1:
                return JsonResponse({
                    'success': False,
                    'message': 'Cannot delete your only address.'
                })

            address.delete()

            return JsonResponse({
                'success': True,
                'message': 'Address deleted successfully!'
            })

        return JsonResponse({
            'success': False,
            'message': 'Invalid request method'
        })
    except Address.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Address not found'
        })


@login_required
def address_set_default(request, address_id):
    """Set an address as the default."""
    try:
        address = Address.objects.get(id=address_id, user=request.user)

        if request.method == 'POST':
            # Update all addresses to not be default
            Address.objects.filter(user=request.user).update(is_default=False)

            # Set this address as default
            address.is_default = True
            address.save()

            return JsonResponse({
                'success': True,
                'message': 'Default address updated successfully!'
            })

        return JsonResponse({
            'success': False,
            'message': 'Invalid request method'
        })
    except Address.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Address not found'
        })


@login_required
def payment_management(request):
    """View for managing user payment methods."""
    # Get all payment methods for the current user
    payment_methods = PaymentMethod.objects.filter(user=request.user)

    context = {
        'payment_methods': payment_methods,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    }

    return render(request, 'account/payment_management.html', context)


@login_required
@require_POST
def payment_create(request):
    """Create a new payment method using Stripe."""
    try:
        data = json.loads(request.body)
        payment_method_id = data.get('payment_method_id')
        payment_method_type = data.get('payment_method_type', 'card')
        set_default = data.get('set_default', False)

        if not payment_method_id:
            return JsonResponse({
                'success': False,
                'message': 'No payment method ID provided.'
            })

        # Create the payment method in our database
        payment_method = create_payment_method(
            user=request.user,
            payment_method_id=payment_method_id,
            payment_method_type=payment_method_type,
            set_default=set_default
        )

        return JsonResponse({
            'success': True,
            'message': 'Payment method added successfully.',
            'payment_method': {
                'id': payment_method.id,
                'display_name': payment_method.display_name,
                'is_default': payment_method.is_default,
                'payment_type': payment_method.get_payment_type_display()
            }
        })

    except stripe.error.CardError as e:
        # Since it's a decline, stripe.error.CardError will be caught
        return JsonResponse({
            'success': False,
            'message': f"Card error: {e.error.message}"
        })
    except stripe.error.RateLimitError:
        # Too many requests made to the API too quickly
        return JsonResponse({
            'success': False,
            'message': "Rate limit exceeded. Please try again later."
        })
    except stripe.error.InvalidRequestError as e:
        # Invalid parameters were supplied to Stripe's API
        return JsonResponse({
            'success': False,
            'message': f"Invalid parameters: {e.error.message}"
        })
    except stripe.error.AuthenticationError:
        # Authentication with Stripe's API failed
        return JsonResponse({
            'success': False,
            'message': "Authentication with payment processor failed."
        })
    except stripe.error.APIConnectionError:
        # Network communication with Stripe failed
        return JsonResponse({
            'success': False,
            'message': "Network error. Please try again."
        })
    except stripe.error.StripeError:
        # Display a very generic error to the user
        return JsonResponse({
            'success': False,
            'message': "Something went wrong. Please try again."
        })
    except Exception as e:
        # Something else happened, completely unrelated to Stripe
        return JsonResponse({
            'success': False,
            'message': f"An error occurred: {str(e)}"
        })


@login_required
@require_POST
def payment_delete(request, payment_id):
    """Delete a payment method."""
    try:
        payment_method = get_object_or_404(PaymentMethod, id=payment_id, user=request.user)

        # Don't allow deleting the default payment method if it's the only one
        if payment_method.is_default and PaymentMethod.objects.filter(user=request.user).count() <= 1:
            return JsonResponse({
                'success': False,
                'message': 'Cannot delete your only payment method.'
            })

        # Delete the payment method
        delete_payment_method(payment_method)

        return JsonResponse({
            'success': True,
            'message': 'Payment method deleted successfully.'
        })

    except stripe.error.StripeError as e:
        return JsonResponse({
            'success': False,
            'message': f"Payment processor error: {str(e)}"
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f"An error occurred: {str(e)}"
        })


@login_required
@require_POST
def payment_set_default(request, payment_id):
    """Set a payment method as the default."""
    try:
        payment_method = get_object_or_404(PaymentMethod, id=payment_id, user=request.user)

        # Set as default
        set_default_payment_method(payment_method)

        return JsonResponse({
            'success': True,
            'message': 'Default payment method updated successfully.'
        })

    except stripe.error.StripeError as e:
        return JsonResponse({
            'success': False,
            'message': f"Payment processor error: {str(e)}"
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f"An error occurred: {str(e)}"
        })


# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def checkout(request):
    """First step of checkout - selecting addresses and shipping method."""
    cart = Cart(request)

    # Check if cart is empty
    if len(cart) == 0:
        messages.warning(request, "Your cart is empty. Please add products before proceeding to checkout.")
        return redirect('cart_detail')

    # Get user's addresses
    addresses = Address.objects.filter(user=request.user)
    default_address = addresses.filter(is_default=True).first() or addresses.first()

    # Get shipping methods
    shipping_methods = ShippingMethod.objects.all()
    default_shipping = shipping_methods.first()  # You might want different logic here

    context = {
        'cart': cart,
        'addresses': addresses,
        'default_address': default_address,
        'shipping_methods': shipping_methods,
        'default_shipping': default_shipping,
        'checkout_step': 1,
    }

    return render(request, 'checkout/checkout_address.html', context)


@login_required
@require_POST
def checkout_address_save(request):
    """Save the selected addresses and shipping method and redirect to payment."""
    try:
        data = json.loads(request.body) if request.body else request.POST

        shipping_address_id = data.get('shipping_address')
        billing_address_id = data.get('billing_address')
        shipping_method_id = data.get('shipping_method')

        # Validate input
        if not shipping_address_id or not shipping_method_id:
            return JsonResponse({
                'success': False,
                'message': 'Shipping address and shipping method are required.'
            })

        # Store in session for later use
        request.session['checkout'] = {
            'shipping_address_id': shipping_address_id,
            'billing_address_id': billing_address_id,
            'shipping_method_id': shipping_method_id,
        }

        return JsonResponse({
            'success': True,
            'redirect_url': reverse('checkout_payment')
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        })


@login_required
def checkout_payment(request):
    """Second step of checkout - payment method selection."""
    cart = Cart(request)

    # Check if cart is empty
    if len(cart) == 0:
        messages.warning(request, "Your cart is empty. Please add products before proceeding to checkout.")
        return redirect('cart_detail')

    # Check if we have the address info
    checkout_data = request.session.get('checkout', {})
    if not checkout_data.get('shipping_address_id') or not checkout_data.get('shipping_method_id'):
        messages.warning(request, "Please select shipping address and method first.")
        return redirect('checkout')

    # Get address and shipping data
    shipping_address = get_object_or_404(Address, id=checkout_data['shipping_address_id'], user=request.user)
    billing_address = None
    if checkout_data.get('billing_address_id'):
        billing_address = get_object_or_404(Address, id=checkout_data['billing_address_id'], user=request.user)
    else:
        billing_address = shipping_address

    shipping_method = get_object_or_404(ShippingMethod, id=checkout_data['shipping_method_id'])

    # Get user's payment methods
    payment_methods = PaymentMethod.objects.filter(user=request.user)
    default_payment = payment_methods.filter(is_default=True).first()

    # Calculate totals
    cart_total = cart.get_total_price()
    shipping_cost = shipping_method.cost
    order_total = cart_total + shipping_cost

    context = {
        'cart': cart,
        'shipping_address': shipping_address,
        'billing_address': billing_address,
        'shipping_method': shipping_method,
        'payment_methods': payment_methods,
        'default_payment': default_payment,
        'cart_total': cart_total,
        'shipping_cost': shipping_cost,
        'order_total': order_total,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'checkout_step': 2,
    }

    return render(request, 'checkout/checkout_payment.html', context)


# Update the create_payment_intent view to handle Decimal conversion properly

@login_required
@require_POST
def create_payment_intent(request):
    """Create a Stripe PaymentIntent and return client secret."""
    try:
        data = json.loads(request.body)
        cart = Cart(request)

        if len(cart) == 0:
            return JsonResponse({
                'success': False,
                'message': 'Your cart is empty.'
            })

        checkout_data = request.session.get('checkout', {})
        if not checkout_data.get('shipping_method_id'):
            return JsonResponse({
                'success': False,
                'message': 'Shipping method not selected.'
            })

        shipping_method = get_object_or_404(ShippingMethod, id=checkout_data['shipping_method_id'])

        # Calculate amount using Decimal for precision
        cart_total = Decimal(str(cart.get_total_price()))
        shipping_cost = shipping_method.cost
        total_amount = cart_total + shipping_cost

        # Convert to cents for Stripe (must be an integer)
        amount = int(total_amount * 100)

        payment_method_id = data.get('payment_method_id')

        # Get or create customer
        customer_id = create_stripe_customer(request.user)

        # Create a PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            customer=customer_id,
            payment_method=payment_method_id,
            confirmation_method='manual',
            confirm=True,
            metadata={
                'user_id': request.user.id,
                'integration_check': 'accept_a_payment',
            },
            receipt_email=request.user.email,
            use_stripe_sdk=True,
            return_url=request.build_absolute_uri(reverse('checkout_complete')),
        )

        # Store payment intent ID in session
        checkout_data['payment_intent_id'] = intent.id
        request.session['checkout'] = checkout_data

        return JsonResponse({
            'success': True,
            'requires_action': intent.status == 'requires_action',
            'payment_intent_client_secret': intent.client_secret,
            'redirect_url': reverse('checkout_complete')
        })

    except stripe.error.CardError as e:
        return JsonResponse({
            'success': False,
            'message': e.error.message
        })
    except stripe.error.StripeError as e:
        return JsonResponse({
            'success': False,
            'message': f"Payment processing error: {str(e)}"
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f"An unexpected error occurred: {str(e)}"
        })

# Update the checkout_complete view to properly handle Decimal conversions
# Make sure you have from decimal import Decimal at the top of your file

@login_required
@transaction.atomic
def checkout_complete(request):
    """Final step of checkout - complete the order."""
    cart = Cart(request)

    # Check if cart is empty
    if len(cart) == 0:
        messages.warning(request, "Your cart is empty. Please add products before proceeding to checkout.")
        return redirect('cart_detail')

    # Get checkout data from session
    checkout_data = request.session.get('checkout', {})
    if not checkout_data:
        messages.warning(request, "Checkout information not found.")
        return redirect('checkout')

    payment_intent_id = checkout_data.get('payment_intent_id')
    if not payment_intent_id:
        messages.warning(request, "Payment information not found.")
        return redirect('checkout_payment')

    try:
        # Retrieve payment intent
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        # Check payment status
        if payment_intent.status != 'succeeded':
            messages.error(request, "Payment was not successful. Please try again.")
            return redirect('checkout_payment')

        # Get address and shipping data
        shipping_address = get_object_or_404(Address, id=checkout_data['shipping_address_id'], user=request.user)
        billing_address_id = checkout_data.get('billing_address_id')
        billing_address = get_object_or_404(Address, id=billing_address_id,
                                            user=request.user) if billing_address_id else shipping_address
        shipping_method = get_object_or_404(ShippingMethod, id=checkout_data['shipping_method_id'])

        # Get payment method
        payment_method = None
        if payment_intent.payment_method:
            try:
                payment_method = PaymentMethod.objects.get(payment_method_id=payment_intent.payment_method)
            except PaymentMethod.DoesNotExist:
                pass  # Will be None, that's OK for now

        # Calculate totals - FIXED to handle Decimal conversion
        cart_total = Decimal(str(cart.get_total_price()))
        shipping_cost = shipping_method.cost
        order_total = cart_total + shipping_cost

        # Create order
        order = Order(
            user=request.user,
            shipping_address=shipping_address,
            billing_address=billing_address,
            payment_method=payment_method,
            shipping_method=shipping_method,
            subtotal=cart_total,
            shipping_cost=shipping_cost,
            total_amount=order_total,
            stripe_payment_intent_id=payment_intent_id,
            stripe_payment_method_id=payment_intent.payment_method if payment_intent.payment_method else None,
            status='processing',
            payment_status='paid'
        )
        order.save()

        # Create order items
        for item in cart:
            product = item['product']

            # Convert price to Decimal if it's not already
            if not isinstance(item['price'], Decimal):
                price = Decimal(str(item['price']))
            else:
                price = item['price']

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                price_at_purchase=price
            )

            # Update product stock
            product.stock_quantity = max(0, product.stock_quantity - item['quantity'])
            product.save()

        # Clear cart
        cart.clear()

        # Clear checkout data
        if 'checkout' in request.session:
            del request.session['checkout']

        # Success message
        messages.success(request, f"Your order #{order.order_number} has been successfully placed!")

        # Redirect to order confirmation
        return render(request, 'checkout/checkout_success.html', {
            'order': order
        })

    except stripe.error.StripeError as e:
        messages.error(request, f"Payment error: {str(e)}")
        return redirect('checkout_payment')
    except Exception as e:
        messages.error(request, f"An error occurred while processing your order: {str(e)}")
        return redirect('checkout')


@login_required
def order_confirmation(request, order_id):
    """Display order confirmation page."""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    return render(request, 'checkout/order_confirmation.html', {
        'order': order
    })


class CustomPasswordResetView(PasswordResetView):
    template_name = 'account/password_reset.html'

    def form_valid(self, form):
        """Override form_valid to add debugging for token generation"""
        # For AJAX requests, handle the success differently
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            email = form.cleaned_data["email"]

            # Call the parent's form_valid which will send the email
            # but store the response first to make sure it completes
            response = super().form_valid(form)

            return JsonResponse({
                'success': True,
                'message': f'If an account with email {email} exists, password reset instructions have been sent.',
                'email': email
            })

        # For non-AJAX, use default behavior
        return super().form_valid(form)

    def form_invalid(self, form):
        # Handle AJAX requests with JSON response
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = error_list
            return JsonResponse({
                'success': False,
                'errors': errors,
                'message': 'Please correct the errors below.'
            }, status=400)
        # For non-AJAX, use default behavior
        return super().form_invalid(form)


class CustomPasswordResetFromKeyView(PasswordResetFromKeyView):
    template_name = 'account/password_reset_from_key.html'
    form_class = CustomResetPasswordKeyForm  # Use our custom form

    def get_success_url(self):
        """Override to return /account/login/ for our use"""
        return '/account/login/'

    def dispatch(self, request, *args, **kwargs):
        # Print session keys for debugging
        print(f"DEBUG: Session keys: {list(request.session.keys())}")

        # Handle the first part - token validation and redirect to set-password URL
        response = super().dispatch(request, *args, **kwargs)

        # After the parent dispatch, check if token_fail was set
        token_fail = getattr(self, 'validlink', None) is False
        print(f"DEBUG: After parent dispatch - token_fail: {token_fail}, validlink: {getattr(self, 'validlink', None)}")

        # If we're using set-password, check if we have the user
        if kwargs.get('key') == 'set-password':
            has_user = hasattr(self, 'reset_user') and self.reset_user is not None
            print(f"DEBUG: In set-password URL, has_user: {has_user}")

            # Explicitly check for the session variable that AllAuth uses
            session_user = request.session.get('_password_reset_key_user', None)
            print(f"DEBUG: _password_reset_key_user in session: {session_user is not None}")

            # If we have no user but the session has it, try to set it
            if not has_user and session_user is not None:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    user_id = session_user[0]
                    self.reset_user = User.objects.get(pk=user_id)
                    print(f"DEBUG: Set reset_user from session: {self.reset_user}")
                    self.validlink = True
                except Exception as e:
                    print(f"DEBUG: Error setting user from session: {str(e)}")
                    self.validlink = False

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Always use validlink attribute for consistency
        token_fail = not getattr(self, 'validlink', False)
        print(f"DEBUG: Setting token_fail={token_fail} in context")
        context['token_fail'] = token_fail

        # Check the state we ended up with
        print(
            f"DEBUG: Final state - validlink: {getattr(self, 'validlink', None)}, reset_user: {hasattr(self, 'reset_user')}")

        return context

    def form_valid(self, form):
        """Override form_valid to return JSON for AJAX requests"""
        print(f"DEBUG: Form valid called, reset_user: {getattr(self, 'reset_user', None)}")

        # For AJAX requests, handle the success differently
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                # Save the new password
                form.save()
                print("DEBUG: Password successfully saved")

                # If we get here, the password was saved successfully
                return JsonResponse({
                    'success': True,
                    'message': 'Your password has been successfully reset! You can now log in with your new password.',
                    'redirect_url': '/account/login/'
                })
            except Exception as e:
                print(f"DEBUG: Error saving password: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': f'An error occurred while resetting your password: {str(e)}'
                }, status=500)

        # For non-AJAX requests, use parent behavior
        response = super().form_valid(form)
        messages.success(self.request, 'Your password has been successfully reset!')
        return redirect('/account/login/')

    def form_invalid(self, form):
        """Override form_invalid to return JSON for AJAX requests"""
        print(f"DEBUG: Form invalid called with errors: {form.errors}")

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {}

            # Get field errors
            for field, error_list in form.errors.items():
                errors[field] = [str(error) for error in error_list]
                print(f"DEBUG: Form error on field {field}: {error_list}")

            # Check for non-field errors (like token issues)
            non_field_errors = []
            if form.non_field_errors():
                non_field_errors = [str(error) for error in form.non_field_errors()]
                print(f"DEBUG: Non-field errors: {non_field_errors}")

            return JsonResponse({
                'success': False,
                'errors': errors,
                'non_field_errors': non_field_errors,
                'message': 'Please correct the errors below.' if errors else
                non_field_errors[0] if non_field_errors else
                'An error occurred during password reset.'
            }, status=400)

        # For non-AJAX requests, use parent behavior
        return super().form_invalid(form)

class SimplePasswordResetForm(forms.Form):
    password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Enter your new password'}),
        required=True
    )
    password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm your new password'}),
        required=True
    )

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("The two password fields didn't match.")
        return password2

    def save(self):
        password = self.cleaned_data["password1"]
        self.user.set_password(password)
        self.user.save()
        return self.user


# Single-step password reset view
class SimplePasswordResetFromKeyView(FormView):
    template_name = 'account/password_reset_from_key.html'
    form_class = SimplePasswordResetForm

    def dispatch(self, request, *args, **kwargs):
        uidb36 = kwargs.get('uidb36')
        key = kwargs.get('key')

        print(f"DEBUG: Simple reset with uidb36={uidb36} and key={key}")

        # Validate the token directly
        try:
            User = get_user_model()
            user_pk = url_str_to_user_pk(uidb36)
            self.user = User.objects.get(pk=user_pk)
            valid = default_token_generator.check_token(self.user, key)

            print(f"DEBUG: Token validation result: {valid}")

            if not valid:
                self.validlink = False
                print("DEBUG: Invalid token")
            else:
                self.validlink = True
                print(f"DEBUG: Valid token for user {self.user}")
        except Exception as e:
            self.validlink = False
            self.user = None
            print(f"DEBUG: Error validating token: {str(e)}")

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass the user to the form
        kwargs['user'] = getattr(self, 'user', None)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['token_fail'] = not getattr(self, 'validlink', False)
        return context

    def form_valid(self, form):
        # For AJAX requests
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                user = form.save()
                print(f"DEBUG: Password successfully reset for {user}")

                return JsonResponse({
                    'success': True,
                    'message': 'Your password has been successfully reset! You can now log in with your new password.',
                    'redirect_url': '/account/login/'
                })
            except Exception as e:
                print(f"DEBUG: Error saving password: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': f'An error occurred while resetting your password: {str(e)}'
                }, status=500)

        # For non-AJAX requests
        form.save()
        messages.success(self.request, 'Your password has been successfully reset!')
        return redirect('/account/login/')

    def form_invalid(self, form):
        print(f"DEBUG: Form errors: {form.errors}")

        # For AJAX requests
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [str(error) for error in error_list]

            return JsonResponse({
                'success': False,
                'errors': errors,
                'message': 'Please correct the errors below.'
            }, status=400)

        # For non-AJAX requests
        return super().form_invalid(form)


def blocked_view(request, *args, **kwargs):
    """Redirect blocked URLs to landing page with message"""
    # You can use different message types:
    # messages.error(request, "Access denied to this page.")
    # messages.info(request, "This feature is currently unavailable.")
    # messages.success(request, "Redirected to home page.")

    messages.warning(request, "Sorry, that page is not available. You've been redirected to the home page.")
    return redirect('landing_page')

# Add this debug view to your views.py to check authentication status