from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Product, Category, StockMovement


class CategoryForm(forms.ModelForm):
    """Form for creating and updating categories"""
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class ProductForm(forms.ModelForm):
    """Form for creating and updating products"""
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'sku', 'barcode', 'description', 'unit', 
            'cost_price', 'selling_price', 'tax_rate', 'stock_quantity',
            'reorder_level', 'status', 'image', 'notes'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'cost_price': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control'}),
            'selling_price': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control'}),
            'tax_rate': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '100', 'class': 'form-control'}),
            'stock_quantity': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control'}),
            'reorder_level': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['status', 'unit']:  # Already set in Meta.widgets
                self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Add help text for SKU and barcode
        self.fields['sku'].help_text = 'Leave blank to auto-generate'
        self.fields['barcode'].help_text = 'Leave blank to auto-generate'
    
    def clean_sku(self):
        """Ensure SKU is unique"""
        sku = self.cleaned_data.get('sku')
        if not sku:
            return sku
            
        qs = Product.objects.filter(sku__iexact=sku)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
            
        if qs.exists():
            raise ValidationError(_('A product with this SKU already exists.'))
            
        return sku.upper()
    
    def clean_barcode(self):
        """Ensure barcode is unique if provided"""
        barcode = self.cleaned_data.get('barcode')
        if not barcode:
            return barcode
            
        qs = Product.objects.filter(barcode__iexact=barcode)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
            
        if qs.exists():
            raise ValidationError(_('A product with this barcode already exists.'))
            
        return barcode
    
    def clean(self):
        """Additional validation"""
        cleaned_data = super().clean()
        cost_price = cleaned_data.get('cost_price')
        selling_price = cleaned_data.get('selling_price')
        
        if cost_price is not None and selling_price is not None:
            if cost_price < 0:
                self.add_error('cost_price', _('Cost price cannot be negative.'))
            if selling_price < 0:
                self.add_error('selling_price', _('Selling price cannot be negative.'))
            if selling_price < cost_price:
                self.add_error('selling_price', _('Selling price cannot be less than cost price.'))
        
        return cleaned_data


class StockAdjustmentForm(forms.ModelForm):
    """Form for adjusting product stock levels"""
    movement_type = forms.ChoiceField(
        choices=StockMovement.MOVEMENT_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Adjustment Type'
    )
    quantity = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label='Quantity',
        help_text='Enter the quantity to add (positive) or remove (negative)'
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        help_text='Optional notes about this adjustment'
    )
    
    class Meta:
        model = StockMovement
        fields = ['movement_type', 'quantity', 'reference', 'notes']
        widgets = {
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set initial movement type if not provided
        if not self.instance.pk and 'movement_type' not in self.data:
            self.fields['movement_type'].initial = 'adjustment'
    
    def save(self, commit=True):
        """Save the stock movement and update product stock"""
        movement = super().save(commit=False)
        
        if self.product:
            movement.product = self.product
            
            # Update product stock based on movement type
            quantity = self.cleaned_data['quantity']
            movement_type = self.cleaned_data['movement_type']
            
            if movement_type in ['purchase', 'in']:
                movement.quantity = abs(quantity)
                self.product.stock_quantity += abs(quantity)
            elif movement_type in ['sale', 'out']:
                movement.quantity = -abs(quantity)
                self.product.stock_quantity = max(0, self.product.stock_quantity - abs(quantity))
            else:  # adjustment
                movement.quantity = quantity
                self.product.stock_quantity = max(0, self.product.stock_quantity + quantity)
            
            # Set created by if user is provided
            if self.user:
                movement.created_by = self.user
                self.product.last_updated_by = self.user
            
            # Save product and movement
            if commit:
                self.product.save()
                movement.save()
        
        return movement


class ProductImportForm(forms.Form):
    """Form for importing products from CSV/Excel"""
    IMPORT_FORMATS = [
        ('csv', 'CSV (Comma Separated Values)'),
        ('xlsx', 'Excel (XLSX)'),
    ]
    
    file = forms.FileField(
        label='Import File',
        help_text='Upload a CSV or Excel file containing product data',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv,.xlsx,.xls'})
    )
    file_format = forms.ChoiceField(
        choices=IMPORT_FORMATS,
        initial='csv',
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Select the format of the file you are importing'
    )
    update_existing = forms.BooleanField(
        required=False,
        initial=True,
        label='Update existing products',
        help_text='Update products that already exist (matched by SKU or barcode)',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean_file(self):
        """Validate the uploaded file"""
        file = self.cleaned_data.get('file')
        if not file:
            raise ValidationError('No file was uploaded.')
        
        # Check file extension
        file_extension = file.name.split('.')[-1].lower()
        if file_extension not in ['csv', 'xlsx', 'xls']:
            raise ValidationError('Invalid file format. Please upload a CSV or Excel file.')
        
        # Check file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if file.size > max_size:
            raise ValidationError(f'File too large. Maximum size is {max_size/1024/1024}MB.')
        
        return file
    
    def process_import(self):
        """Process the imported file"""
        import pandas as pd
        from io import StringIO, BytesIO
        
        file = self.cleaned_data['file']
        file_format = self.cleaned_data['file_format']
        update_existing = self.cleaned_data['update_existing']
        
        # Read the file based on format
        if file_format == 'csv':
            # For CSV, read as text first to handle encoding
            content = file.read().decode('utf-8-sig')
            df = pd.read_csv(StringIO(content))
        else:  # Excel
            df = pd.read_excel(file)
        
        # Normalize column names (lowercase, replace spaces with underscores)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        # Required columns
        required_columns = ['name', 'category', 'cost_price', 'selling_price']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValidationError(f'Missing required columns: {", ".join(missing_columns)}')
        
        # Initialize counters
        imported = 0
        updated = 0
        skipped = 0
        errors = []
        
        # Process each row
        for index, row in df.iterrows():
            try:
                # Get or create category
                category_name = str(row.get('category', '')).strip()
                if not category_name:
                    errors.append(f'Row {index+2}: Category is required')
                    skipped += 1
                    continue
                
                category, created = Category.objects.get_or_create(
                    name=category_name,
                    defaults={'created_by': self.user}
                )
                
                # Check for existing product
                sku = str(row.get('sku', '')).strip()
                barcode = str(row.get('barcode', '')).strip()
                
                # Try to find existing product by SKU or barcode
                existing_product = None
                if sku:
                    existing_product = Product.objects.filter(sku__iexact=sku).first()
                if not existing_product and barcode:
                    existing_product = Product.objects.filter(barcode__iexact=barcode).first()
                
                # Prepare product data
                product_data = {
                    'name': str(row.get('name', '')).strip(),
                    'category': category,
                    'description': str(row.get('description', '')).strip(),
                    'sku': sku or None,
                    'barcode': barcode or None,
                    'unit': str(row.get('unit', 'pcs')).strip().lower(),
                    'cost_price': float(row.get('cost_price', 0)),
                    'selling_price': float(row.get('selling_price', 0)),
                    'tax_rate': float(row.get('tax_rate', 0)),
                    'reorder_level': int(float(row.get('reorder_level', 0))),
                    'stock_quantity': int(float(row.get('stock_quantity', 0))),
                    'is_active': bool(row.get('is_active', True)),
                    'last_updated_by': self.user,
                }
                
                # Update or create product
                if existing_product and update_existing:
                    # Update existing product
                    for key, value in product_data.items():
                        setattr(existing_product, key, value)
                    existing_product.save()
                    updated += 1
                else:
                    # Create new product
                    product_data['created_by'] = self.user
                    Product.objects.create(**product_data)
                    imported += 1
                
            except Exception as e:
                errors.append(f'Row {index+2}: {str(e)}')
                skipped += 1
        
        # Save import results
        self.imported = imported
        self.updated = updated
        self.skipped = skipped
        self.errors = errors
        
        return {
            'imported': imported,
            'updated': updated,
            'skipped': skipped,
            'errors': errors,
        }
