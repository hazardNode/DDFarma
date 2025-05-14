# core/views.py
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import resolve, reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import Product
from .cart import Cart
from core.models import Product, Order, Category, User, ProductImage
from core.forms import ProductForm, CategoryForm, UserForm, UserProfileForm, ProductImageForm, MultipleImageUploadForm
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


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
        'is_create': True  # Flag to indicate this is a create form
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
        'is_create': False
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
    return render(request, 'core/management/form.html', {'form': form})

def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'core/management/form.html', {'form': form})

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
    return render(request, 'core/management/form.html', {'form': form})

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

