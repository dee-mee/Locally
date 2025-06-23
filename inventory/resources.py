from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from .models import Product, Category, Supplier, ProductTag

class ProductResource(resources.ModelResource):
    """Resource for importing/exporting products"""
    
    # Handle foreign key and many-to-many relationships
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, 'name')
    )
    
    supplier = fields.Field(
        column_name='supplier',
        attribute='supplier',
        widget=ForeignKeyWidget(Supplier, 'name')
    )
    
    tags = fields.Field(
        column_name='tags',
        attribute='tags',
        widget=ManyToManyWidget(ProductTag, field='name', separator=',')
    )
    
    class Meta:
        model = Product
        fields = (
            'id', 'name', 'sku', 'barcode', 'description', 'category',
            'cost_price', 'selling_price', 'taxable', 'tax_rate',
            'track_inventory', 'stock_quantity', 'reorder_level', 'status',
            'weight', 'weight_unit', 'length', 'width', 'height',
            'brand', 'supplier', 'tags', 'alert_low_stock',
            'allow_backorder', 'is_active', 'notes', 'created_at', 'updated_at'
        )
        export_order = fields
        import_id_fields = ('sku',)  # Use SKU as the unique identifier
        skip_unchanged = True
        report_skipped = True
        
    def before_import_row(self, row, **kwargs):
        """Handle data before importing each row"""
        # Handle boolean fields
        for field in ['taxable', 'track_inventory', 'alert_low_stock', 'allow_backorder', 'is_active']:
            if field in row:
                if isinstance(row[field], str):
                    row[field] = row[field].lower() in ('true', 'yes', '1', 't')
                elif row[field] is None:
                    row[field] = False
        
        # Ensure required fields have default values
        if 'status' not in row or not row['status']:
            row['status'] = 'active'
            
        # Handle optional fields
        optional_fields = ['supplier', 'brand', 'weight', 'length', 'width', 'height', 'notes']
        for field in optional_fields:
            if field in row and row[field] in ('', None):
                row[field] = None
                
        # Set default weight unit if not provided
        if 'weight_unit' not in row or not row['weight_unit']:
            row['weight_unit'] = 'kg'
            
    def after_import_row(self, row, row_result, row_number=None, **kwargs):
        """Handle data after importing each row"""
        # You can add any post-processing here if needed
        pass

class CategoryResource(resources.ModelResource):
    """Resource for importing/exporting categories"""
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'slug', 'created_at', 'updated_at')
        export_order = fields
        import_id_fields = ('name',)  # Use name as the unique identifier
        skip_unchanged = True
        report_skipped = True

class SupplierResource(resources.ModelResource):
    """Resource for importing/exporting suppliers"""
    
    class Meta:
        model = Supplier
        fields = ('id', 'name', 'contact_person', 'email', 'phone', 'address', 'website', 'notes', 'is_active', 'created_at', 'updated_at')
        export_order = fields
        import_id_fields = ('name',)  # Use name as the unique identifier
        skip_unchanged = True
        report_skipped = True
