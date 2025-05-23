# Create a new file: core/error_handlers.py

from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
import logging

logger = logging.getLogger(__name__)


def handler404(request, exception):
    """Custom 404 error handler"""
    messages.error(request, "Oops! The page you're looking for doesn't exist. You've been redirected to the home page.")
    logger.warning(f"404 error: {request.path} - User: {request.user}")
    return redirect('landing_page')


def handler403(request, exception):
    """Custom 403 error handler"""
    messages.warning(request, "Access denied! You don't have permission to view that page.")
    logger.warning(f"403 error: {request.path} - User: {request.user}")
    return redirect('landing_page')


def handler500(request):
    """Custom 500 error handler"""
    messages.error(request,
                   "Something went wrong on our end. We're working to fix it. You've been redirected to the home page.")
    logger.error(f"500 error: {request.path} - User: {request.user}")
    return redirect('landing_page')


def handler400(request, exception):
    """Custom 400 error handler"""
    messages.error(request, "Bad request. The data you sent couldn't be processed.")
    logger.warning(f"400 error: {request.path} - User: {request.user}")
    return redirect('landing_page')


# Alternative: If you want to handle all errors with one function
def generic_error_handler(request, status_code, message):
    """Generic error handler for all HTTP errors"""
    error_messages = {
        400: "Bad request. Please check your input and try again.",
        401: "Authentication required. Please log in to access this page.",
        403: "Access denied! You don't have permission to view that page.",
        404: "Oops! The page you're looking for doesn't exist.",
        405: "Method not allowed for this page.",
        429: "Too many requests. Please slow down and try again later.",
        500: "Something went wrong on our end. We're working to fix it.",
        502: "Server temporarily unavailable. Please try again later.",
        503: "Service temporarily unavailable. Please try again later.",
    }

    default_message = "An error occurred. You've been redirected to the home page."
    error_message = error_messages.get(status_code, default_message)

    # Add custom message if provided
    if message:
        error_message = f"{message} You've been redirected to the home page."
    else:
        error_message = f"{error_message} You've been redirected to the home page."

    # Choose message type based on error code
    if status_code in [500, 502, 503]:
        messages.error(request, error_message)
    elif status_code in [401, 403]:
        messages.warning(request, error_message)
    else:
        messages.info(request, error_message)

    logger.warning(f"{status_code} error: {request.path} - User: {request.user}")
    return redirect('landing_page')