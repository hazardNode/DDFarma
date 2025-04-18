# core/views.py
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import resolve

from core.models import Product, Order, Category, User
from core.forms import ProductForm, CategoryForm, UserForm


def product_list(request):
    products = Product.objects.all()
    return render(request, 'core/management/product_list.html', {'products': products})

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'core/management/form.html', {'form': form})

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'core/management/form.html', {'form': form})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'core/management/product_confirm_delete.html', {'object': product})

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
    products = Product.objects.filter(is_active=True)

    # Organize products by category
    context = {
        'categories': categories,
        'products_by_category': {
            category: products.filter(category=category)
            for category in categories
        }
    }
    return render(request, 'core/shop.html', context)
