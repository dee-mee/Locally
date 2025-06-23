# Import views to make them available at the package level
from .receipt_views import view_receipt, print_receipt

# For backward compatibility and to make them available via from pos import *
__all__ = ['view_receipt', 'print_receipt']