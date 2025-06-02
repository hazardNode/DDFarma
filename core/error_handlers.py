# core/error_handlers.py

from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
import logging

logger = logging.getLogger(__name__)


def safe_add_message(request, level, message):
    """
    Safely add a message, handling cases where messages framework isn't available
    """
    try:
        # Check if request has session and messages middleware is available
        if (hasattr(request, 'session') and
            hasattr(request, '_messages') and
            request.session.session_key):

            if level == 'error':
                messages.error(request, message)
            elif level == 'warning':
                messages.warning(request, message)
            elif level == 'info':
                messages.info(request, message)
            else:
                messages.info(request, message)
        else:
            # If messages aren't available, just log it
            logger.info(f"Could not add {level} message: {message}")
    except Exception as e:
        # If anything goes wrong with messages, just log and continue
        logger.error(f"Error adding message: {e}")


def handler404(request, exception):
    """Custom 404 error handler"""
    safe_add_message(request, 'error',
                    "¡Oops! La página que buscas no existe. Has sido redirigido a la página de inicio.")
    logger.warning(f"404 error: {request.path} - User: {getattr(request, 'user', 'Anonymous')}")
    return redirect('landing_page')


def handler403(request, exception):
    """Custom 403 error handler"""
    safe_add_message(request, 'warning',
                    "¡Acceso denegado! No tienes permisos para ver esa página.")
    logger.warning(f"403 error: {request.path} - User: {getattr(request, 'user', 'Anonymous')}")
    return redirect('landing_page')


def handler500(request):
    """Custom 500 error handler"""
    safe_add_message(request, 'error',
                    "Algo salió mal de nuestro lado. Estamos trabajando para solucionarlo. Has sido redirigido a la página de inicio.")
    logger.error(f"500 error: {request.path} - User: {getattr(request, 'user', 'Anonymous')}")
    return redirect('landing_page')


def handler400(request, exception):
    """Custom 400 error handler"""
    safe_add_message(request, 'error',
                    "Solicitud incorrecta. Los datos que enviaste no pudieron ser procesados.")
    logger.warning(f"400 error: {request.path} - User: {getattr(request, 'user', 'Anonymous')}")
    return redirect('landing_page')


def generic_error_handler(request, status_code, message=None):
    """Generic error handler for all HTTP errors"""
    error_messages = {
        400: "Solicitud incorrecta. Por favor verifica tu entrada e intenta de nuevo.",
        401: "Autenticación requerida. Por favor inicia sesión para acceder a esta página.",
        403: "¡Acceso denegado! No tienes permisos para ver esa página.",
        404: "¡Oops! La página que buscas no existe.",
        405: "Método no permitido para esta página.",
        429: "Demasiadas solicitudes. Por favor reduce la velocidad e intenta más tarde.",
        500: "Algo salió mal de nuestro lado. Estamos trabajando para solucionarlo.",
        502: "Servidor temporalmente no disponible. Por favor intenta más tarde.",
        503: "Servicio temporalmente no disponible. Por favor intenta más tarde.",
    }

    default_message = "Ocurrió un error. Has sido redirigido a la página de inicio."
    error_message = error_messages.get(status_code, default_message)

    # Add custom message if provided
    if message:
        error_message = f"{message} Has sido redirigido a la página de inicio."
    else:
        error_message = f"{error_message} Has sido redirigido a la página de inicio."

    # Choose message type and level based on error code
    if status_code in [500, 502, 503]:
        message_level = 'error'
    elif status_code in [401, 403]:
        message_level = 'warning'
    else:
        message_level = 'info'

    safe_add_message(request, message_level, error_message)
    logger.warning(f"{status_code} error: {request.path} - User: {getattr(request, 'user', 'Anonymous')}")

    return redirect('landing_page')