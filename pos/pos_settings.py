"""
POS (Point of Sale) Settings

This module contains all the configurable settings for the POS application.
These settings can be overridden in your project's settings.py file.
"""

from django.conf import settings

# Default tax rate (in percentage)
DEFAULT_TAX_RATE = getattr(settings, 'POS_DEFAULT_TAX_RATE', 10.0)

# Default currency symbol
CURRENCY = getattr(settings, 'POS_CURRENCY', '$')

# Number of decimal places for currency
CURRENCY_DECIMALS = getattr(settings, 'POS_CURRENCY_DECIMALS', 2)

# Number of items per page in the product grid
ITEMS_PER_PAGE = getattr(settings, 'POS_ITEMS_PER_PAGE', 24)

# Enable/disable barcode scanner
ENABLE_BARCODE_SCANNER = getattr(settings, 'POS_ENABLE_BARCODE_SCANNER', True)

# Barcode scanner types to support
# Options: 'upc', 'ean13', 'code128', 'code39', 'qr'
BARCODE_TYPES = getattr(settings, 'POS_BARCODE_TYPES', ['upc', 'ean13', 'code128', 'code39', 'qr'])

# Enable/disable customer management in POS
ENABLE_CUSTOMER_MANAGEMENT = getattr(settings, 'POS_ENABLE_CUSTOMER_MANAGEMENT', True)

# Enable/disable discounting
ENABLE_DISCOUNTS = getattr(settings, 'POS_ENABLE_DISCOUNTS', True)

# Default discount types
DISCOUNT_TYPES = getattr(settings, 'POS_DISCOUNT_TYPES', [
    ('percentage', 'Percentage'),
    ('fixed', 'Fixed Amount'),
])

# Maximum discount percentage allowed (0-100)
MAX_DISCOUNT_PERCENTAGE = getattr(settings, 'POS_MAX_DISCOUNT_PERCENTAGE', 100)

# Enable/disable order notes
ENABLE_ORDER_NOTES = getattr(settings, 'POS_ENABLE_ORDER_NOTES', True)

# Enable/disable order printing
ENABLE_PRINTING = getattr(settings, 'POS_ENABLE_PRINTING', True)

# Default printer name or IP
DEFAULT_PRINTER = getattr(settings, 'POS_DEFAULT_PRINTER', None)

# Receipt template to use
RECEIPT_TEMPLATE = getattr(settings, 'POS_RECEIPT_TEMPLATE', 'pos/includes/receipt.html')

# Enable/disable cash drawer
ENABLE_CASH_DRAWER = getattr(settings, 'POS_ENABLE_CASH_DRAWER', False)

# Cash drawer GPIO pin (for Raspberry Pi)
CASH_DRAWER_GPIO_PIN = getattr(settings, 'POS_CASH_DRAWER_GPIO_PIN', 17)

# Enable/disable inventory management
ENABLE_INVENTORY_MANAGEMENT = getattr(settings, 'POS_ENABLE_INVENTORY_MANAGEMENT', True)

# Auto update inventory when order is completed
AUTO_UPDATE_INVENTORY = getattr(settings, 'POS_AUTO_UPDATE_INVENTORY', True)

# Allow selling out of stock items
ALLOW_OUT_OF_STOCK = getattr(settings, 'POS_ALLOW_OUT_OF_STOCK', False)

# Show stock levels in POS
SHOW_STOCK_LEVELS = getattr(settings, 'POS_SHOW_STOCK_LEVELS', True)

# Low stock threshold
LOW_STOCK_THRESHOLD = getattr(settings, 'POS_LOW_STOCK_THRESHOLD', 5)

# Enable/disable price lookup
ENABLE_PRICE_LOOKUP = getattr(settings, 'POS_ENABLE_PRICE_LOOKUP', True)

# Default payment methods
PAYMENT_METHODS = getattr(settings, 'POS_PAYMENT_METHODS', [
    ('cash', 'Cash'),
    ('card', 'Credit/Debit Card'),
    ('mobile', 'Mobile Payment'),
    ('other', 'Other'),
])

# Default currency position
# Options: 'left', 'right', 'left_with_space', 'right_with_space'
CURRENCY_POSITION = getattr(settings, 'POS_CURRENCY_POSITION', 'left')

# Date format to use in the POS interface
DATE_FORMAT = getattr(settings, 'POS_DATE_FORMAT', 'Y-m-d')

# Time format to use in the POS interface
TIME_FORMAT = getattr(settings, 'POS_TIME_FORMAT', 'H:i:s')

# Date/time format for receipts
RECEIPT_DATETIME_FORMAT = getattr(settings, 'POS_RECEIPT_DATETIME_FORMAT', 'M d, Y H:i')

# Enable/disable order history
ENABLE_ORDER_HISTORY = getattr(settings, 'POS_ENABLE_ORDER_HISTORY', True)

# Number of recent orders to show in the history
RECENT_ORDERS_LIMIT = getattr(settings, 'POS_RECENT_ORDERS_LIMIT', 10)

# Enable/disable order search
ENABLE_ORDER_SEARCH = getattr(settings, 'POS_ENABLE_ORDER_SEARCH', True)

# Enable/disable order returns
ENABLE_ORDER_RETURNS = getattr(settings, 'POS_ENABLE_ORDER_RETURNS', True)

# Enable/disable order voiding
ENABLE_ORDER_VOIDING = getattr(settings, 'POS_ENABLE_ORDER_VOIDING', True)

# Enable/disable order editing
ENABLE_ORDER_EDITING = getattr(settings, 'POS_ENABLE_ORDER_EDITING', True)

# Enable/disable order splitting
ENABLE_ORDER_SPLITTING = getattr(settings, 'POS_ENABLE_ORDER_SPLITTING', True)

# Enable/disable order hold/resume
ENABLE_ORDER_HOLD = getattr(settings, 'POS_ENABLE_ORDER_HOLD', True)

# Maximum number of held orders
MAX_HELD_ORDERS = getattr(settings, 'POS_MAX_HELD_ORDERS', 10)

# Enable/disable order printing
ENABLE_ORDER_PRINTING = getattr(settings, 'POS_ENABLE_ORDER_PRINTING', True)

# Enable/disable email receipts
ENABLE_EMAIL_RECEIPTS = getattr(settings, 'POS_ENABLE_EMAIL_RECEIPTS', True)

# Enable/disable SMS receipts
ENABLE_SMS_RECEIPTS = getattr(settings, 'POS_ENABLE_SMS_RECEIPTS', True)

# Default receipt message
DEFAULT_RECEIPT_MESSAGE = getattr(settings, 'POS_DEFAULT_RECEIPT_MESSAGE', 
    'Thank you for your purchase!\nPlease come again.')

# Enable/disable tips
ENABLE_TIPS = getattr(settings, 'POS_ENABLE_TIPS', True)

# Default tip percentages
DEFAULT_TIP_PERCENTAGES = getattr(settings, 'POS_DEFAULT_TIP_PERCENTAGES', [10, 15, 20])

# Enable/disable service charges
ENABLE_SERVICE_CHARGE = getattr(settings, 'POS_ENABLE_SERVICE_CHARGE', False)

# Default service charge (percentage)
DEFAULT_SERVICE_CHARGE = getattr(settings, 'POS_DEFAULT_SERVICE_CHARGE', 0.0)

# Enable/disable table management
ENABLE_TABLE_MANAGEMENT = getattr(settings, 'POS_ENABLE_TABLE_MANAGEMENT', False)

# Enable/disable multi-store support
ENABLE_MULTI_STORE = getattr(settings, 'POS_ENABLE_MULTI_STORE', False)

# Enable/disable user permissions
ENABLE_USER_PERMISSIONS = getattr(settings, 'POS_ENABLE_USER_PERMISSIONS', True)

# Enable/disable shift management
ENABLE_SHIFT_MANAGEMENT = getattr(settings, 'POS_ENABLE_SHIFT_MANAGEMENT', True)

# Enable/disable cash management
ENABLE_CASH_MANAGEMENT = getattr(settings, 'POS_ENABLE_CASH_MANAGEMENT', True)

# Enable/disable expense tracking
ENABLE_EXPENSE_TRACKING = getattr(settings, 'POS_ENABLE_EXPENSE_TRACKING', True)

# Enable/disable reporting
ENABLE_REPORTING = getattr(settings, 'POS_ENABLE_REPORTING', True)

# Enable/disable dashboard
ENABLE_DASHBOARD = getattr(settings, 'POS_ENABLE_DASHBOARD', True)

# Dashboard refresh interval in seconds
DASHBOARD_REFRESH_INTERVAL = getattr(settings, 'POS_DASHBOARD_REFRESH_INTERVAL', 60)

# Enable/disable offline mode
ENABLE_OFFLINE_MODE = getattr(settings, 'POS_ENABLE_OFFLINE_MODE', False)

# Enable/disable auto backup
ENABLE_AUTO_BACKUP = getattr(settings, 'POS_ENABLE_AUTO_BACKUP', True)

# Backup interval in minutes
BACKUP_INTERVAL = getattr(settings, 'POS_BACKUP_INTERVAL', 60)

# Number of backups to keep
MAX_BACKUPS = getattr(settings, 'POS_MAX_BACKUPS', 30)

# Enable/disable cloud sync
ENABLE_CLOUD_SYNC = getattr(settings, 'POS_ENABLE_CLOUD_SYNC', False)

# Cloud sync interval in minutes
CLOUD_SYNC_INTERVAL = getattr(settings, 'POS_CLOUD_SYNC_INTERVAL', 15)

# Enable/disable updates
ENABLE_UPDATES = getattr(settings, 'POS_ENABLE_UPDATES', True)

# Check for updates interval in hours
UPDATE_CHECK_INTERVAL = getattr(settings, 'POS_UPDATE_CHECK_INTERVAL', 24)

# Enable/disable debug mode
DEBUG = getattr(settings, 'POS_DEBUG', settings.DEBUG)

# Log file path
LOG_FILE = getattr(settings, 'POS_LOG_FILE', 'pos.log')

# Log level
LOG_LEVEL = getattr(settings, 'POS_LOG_LEVEL', 'INFO')

# Maximum log file size in MB
MAX_LOG_SIZE = getattr(settings, 'POS_MAX_LOG_SIZE', 10)

# Number of log files to keep
LOG_BACKUP_COUNT = getattr(settings, 'POS_LOG_BACKUP_COUNT', 5)

# Enable/disable API
ENABLE_API = getattr(settings, 'POS_ENABLE_API', True)

# API authentication classes
API_AUTHENTICATION_CLASSES = getattr(settings, 'POS_API_AUTHENTICATION_CLASSES', [
    'rest_framework.authentication.SessionAuthentication',
    'rest_framework.authentication.BasicAuthentication',
    'rest_framework_simplejwt.authentication.JWTAuthentication',
])

# API permission classes
API_PERMISSION_CLASSES = getattr(settings, 'POS_API_PERMISSION_CLASSES', [
    'rest_framework.permissions.IsAuthenticated',
])

# API pagination class
API_PAGINATION_CLASS = getattr(settings, 'POS_API_PAGINATION_CLASS', 
    'rest_framework.pagination.PageNumberPagination')

# API page size
API_PAGE_SIZE = getattr(settings, 'POS_API_PAGE_SIZE', 50)

# Enable/disable Swagger/ReDoc documentation
ENABLE_API_DOCS = getattr(settings, 'POS_ENABLE_API_DOCS', True)

# Enable/disable CORS
ENABLE_CORS = getattr(settings, 'POS_ENABLE_CORS', False)

# CORS allowed origins
CORS_ALLOWED_ORIGINS = getattr(settings, 'POS_CORS_ALLOWED_ORIGINS', [])

# Enable/disable CSRF protection
ENABLE_CSRF = getattr(settings, 'POS_ENABLE_CSRF', True)

# Enable/disable HTTPS
ENABLE_HTTPS = getattr(settings, 'POS_ENABLE_HTTPS', not DEBUG)

# Session timeout in seconds
SESSION_TIMEOUT = getattr(settings, 'POS_SESSION_TIMEOUT', 1800)  # 30 minutes

# Enable/disable remember me
ENABLE_REMEMBER_ME = getattr(settings, 'POS_ENABLE_REMEMBER_ME', True)

# Remember me duration in days
REMEMBER_ME_DURATION = getattr(settings, 'POS_REMEMBER_ME_DURATION', 30)

# Enable/disable password reset
ENABLE_PASSWORD_RESET = getattr(settings, 'POS_ENABLE_PASSWORD_RESET', True)

# Enable/disable user registration
ENABLE_REGISTRATION = getattr(settings, 'POS_ENABLE_REGISTRATION', False)

# Enable/disable email verification
ENABLE_EMAIL_VERIFICATION = getattr(settings, 'POS_ENABLE_EMAIL_VERIFICATION', False)

# Enable/disable two-factor authentication
ENABLE_2FA = getattr(settings, 'POS_ENABLE_2FA', False)

# Default timezone
TIME_ZONE = getattr(settings, 'POS_TIME_ZONE', settings.TIME_ZONE)

# Default language code
LANGUAGE_CODE = getattr(settings, 'POS_LANGUAGE_CODE', settings.LANGUAGE_CODE)

# Available languages
LANGUAGES = getattr(settings, 'POS_LANGUAGES', [
    ('en', 'English'),
    ('es', 'Spanish'),
    ('fr', 'French'),
    ('de', 'German'),
    ('it', 'Italian'),
    ('pt', 'Portuguese'),
    ('ru', 'Russian'),
    ('zh-hans', 'Simplified Chinese'),
    ('ja', 'Japanese'),
    ('ko', 'Korean'),
    ('ar', 'Arabic'),
    ('hi', 'Hindi'),
])

# Enable/disable translation
ENABLE_TRANSLATION = getattr(settings, 'POS_ENABLE_TRANSLATION', True)

# Enable/disable RTL support
ENABLE_RTL = getattr(settings, 'POS_ENABLE_RTL', False)

# Default theme
DEFAULT_THEME = getattr(settings, 'POS_DEFAULT_THEME', 'light')

# Available themes
THEMES = getattr(settings, 'POS_THEMES', [
    ('light', 'Light'),
    ('dark', 'Dark'),
    ('system', 'System'),
])

# Enable/disable theme switching
ENABLE_THEME_SWITCHING = getattr(settings, 'POS_ENABLE_THEME_SWITCHING', True)

# Enable/disable animations
ENABLE_ANIMATIONS = getattr(settings, 'POS_ENABLE_ANIMATIONS', True)

# Enable/disable notifications
ENABLE_NOTIFICATIONS = getattr(settings, 'POS_ENABLE_NOTIFICATIONS', True)

# Enable/disable sounds
ENABLE_SOUNDS = getattr(settings, 'POS_ENABLE_SOUNDS', True)

# Default sound theme
DEFAULT_SOUND_THEME = getattr(settings, 'POS_DEFAULT_SOUND_THEME', 'default')

# Available sound themes
SOUND_THEMES = getattr(settings, 'POS_SOUND_THEMES', [
    ('default', 'Default'),
    ('minimal', 'Minimal'),
    ('none', 'None'),
])

# Enable/disable keyboard shortcuts
ENABLE_KEYBOARD_SHORTCUTS = getattr(settings, 'POS_ENABLE_KEYBOARD_SHORTCUTS', True)

# Custom keyboard shortcuts
KEYBOARD_SHORTCUTS = getattr(settings, 'POS_KEYBOARD_SHORTCUTS', {
    'new_order': 'ctrl+n',
    'search': '/',
    'barcode': 'f2',
    'checkout': 'f9',
    'cancel': 'esc',
    'save': 'ctrl+s',
    'print': 'ctrl+p',
    'help': 'f1',
})

# Enable/disable auto-complete
ENABLE_AUTOCOMPLETE = getattr(settings, 'POS_ENABLE_AUTOCOMPLETE', True)

# Auto-complete delay in milliseconds
AUTOCOMPLETE_DELAY = getattr(settings, 'POS_AUTOCOMPLETE_DELAY', 300)

# Enable/disable form validation
ENABLE_FORM_VALIDATION = getattr(settings, 'POS_ENABLE_FORM_VALIDATION', True)

# Enable/disable form auto-save
ENABLE_AUTO_SAVE = getattr(settings, 'POS_ENABLE_AUTO_SAVE', True)

# Auto-save interval in seconds
AUTO_SAVE_INTERVAL = getattr(settings, 'POS_AUTO_SAVE_INTERVAL', 60)

# Enable/disable auto-logout
ENABLE_AUTO_LOGOUT = getattr(settings, 'POS_ENABLE_AUTO_LOGOUT', True)

# Auto-logout warning in seconds
AUTO_LOGOUT_WARNING = getattr(settings, 'POS_AUTO_LOGOUT_WARNING', 60)

# Auto-logout timeout in seconds
AUTO_LOGOUT_TIMEOUT = getattr(settings, 'POS_AUTO_LOGOUT_TIMEOUT', 300)

# Enable/disable session timeout warning
ENABLE_SESSION_TIMEOUT_WARNING = getattr(settings, 'POS_ENABLE_SESSION_TIMEOUT_WARNING', True)

# Session timeout warning in seconds
SESSION_TIMEOUT_WARNING = getattr(settings, 'POS_SESSION_TIMEOUT_WARNING', 60)

# Enable/disable idle timeout
ENABLE_IDLE_TIMEOUT = getattr(settings, 'POS_ENABLE_IDLE_TIMEOUT', True)

# Idle timeout in seconds
IDLE_TIMEOUT = getattr(settings, 'POS_IDLE_TIMEOUT', 900)  # 15 minutes

# Enable/disable screen lock
ENABLE_SCREEN_LOCK = getattr(settings, 'POS_ENABLE_SCREEN_LOCK', True)

# Screen lock timeout in seconds
SCREEN_LOCK_TIMEOUT = getattr(settings, 'POS_SCREEN_LOCK_TIMEOUT', 300)  # 5 minutes
