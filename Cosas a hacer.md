✅ FASE 1: Funcionalidad mínima completa
Objetivo: que el ecommerce funcione de principio a fin.

- Añadir nombre y apellidos en el perfil del usuario (Hecho, Falta hacerlo Bonito)

- Confirmación por email con Allauth (A la espera de GoDaddy)

- Sistema de cambio de email (arreglar flujos y validación)

- Pasarela de pagos: Stripe básica

- Guardar dirección de envío en la pasarela y asociarla al usuario

- Añadir códigos de descuento en el checkout

- PDF de factura adaptado a formato español (IVA, NIF, etc.) 

Enviar correos al pagar:

- Albarán al almacén

- Aviso al admin

- Confirmación al usuario

- Página “¿Quiénes somos?” (opcional, pero es muy simple de hacer y ayuda)

🔒 FASE 2: Seguridad y robustez
Objetivo: proteger el sistema, blindar accesos, evitar errores graves.

- Blindar el acceso a rutas de Allauth (login, cambio de contraseña, etc.)

- Asegurar cambio de correo (verificación, bloqueo temporal, doble confirmación si hace falta)

- Integrar pago por cuenta bancaria (SEPA u otro método)

- Seguimiento de pedidos (integración con empresa externa, y correo al usuario)

🎨 FASE 3: Estética y experiencia
Objetivo: mejorar experiencia del usuario y apariencia profesional.

- Interfaz de usuario con Tailwind: revisar colores, márgenes, botones, errores

- Multilenguaje (i18n): español/inglés con gettext y plantilla base traducible

- Varias imágenes por producto + galería con thumbnails y selección activa