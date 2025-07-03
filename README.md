# DDFarma - Django E-commerce Platform

A Django-based e-commerce platform for pharmaceutical/medical supplies with comprehensive product management, order processing, and payment integration.

## Features

### Core Functionality
- **Product Management**: Full CRUD operations for products with multi-image support
- **Order Processing**: Complete order lifecycle from cart to delivery
- **Payment Integration**: Stripe payment processing with multiple payment methods
- **User Management**: Custom user model with role-based access control
- **Inventory Management**: Stock tracking and management

### Authentication & Accounts
- Custom authentication using django-allauth
- Email verification and password reset
- User profile management
- Address and payment method management

### Management Dashboard
- Product catalog administration
- Order management and tracking
- User administration
- Receipt generation and bulk download

## Tech Stack

- **Backend**: Django 5.1.7
- **Database**: PostgreSQL
- **Authentication**: django-allauth
- **Payments**: Stripe
- **Email**: Office365 SMTP
- **File Storage**: Local media files with secure serving

## Installation

1. Clone the repository

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create `.env` file with:
   ```
   DB_NAME=django_ecommerce
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   EMAIL_HOST_USER=your_email@domain.com
   EMAIL_HOST_PASSWORD=your_password
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   ```

4. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run server:
   ```bash
   python manage.py runserver
   ```

## Dependencies

Main packages from `requirements.txt`:
- Django 5.1.7
- django-allauth 65.6.0
- django-environ 0.12.0
- django-extensions 3.2.3
- django-widget-tweaks 1.5.0
- psycopg2-binary 2.9.10
- Pillow 11.2.1
- stripe 12.1.0
- reportlab 4.4.0
- requests 2.32.3

## Key URLs

- `/` - Landing page
- `/shop/` - Product catalog
- `/cart/` - Shopping cart
- `/checkout/` - Checkout process
- `/account/` - User account management
- `/management/` - Admin dashboard

## Models Overview

- **User**: Custom user model with roles
- **Product**: Product catalog with categories and images
- **Order**: Order processing with items and payment tracking
- **Address**: User shipping/billing addresses
- **PaymentMethod**: Stripe payment method storage
- **Receipt**: Order receipt generation

## Security Features

- Role-based access control
- Secure media file serving
- CSRF protection
- XSS protection
- Input validation and sanitization
