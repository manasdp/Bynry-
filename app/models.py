from app import db
from sqlalchemy.orm import relationship

# Association table for bundles (many-to-many self-join on Product)
bundle_components = db.Table('bundle_components',
    db.Column('bundle_product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True),
    db.Column('component_product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True),
    db.Column('quantity_in_bundle', db.Integer, nullable=False)
)

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    warehouses = relationship("Warehouse", back_populates="company")
    products = relationship("Product", back_populates="company")

class Warehouse(db.Model):
    __tablename__ = 'warehouses'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    company = relationship("Company", back_populates="warehouses")

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    contact_email = db.Column(db.String(255))

class ProductType(db.Model):
    __tablename__ = 'product_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    low_stock_threshold = db.Column(db.Integer, nullable=False, default=10)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    product_type_id = db.Column(db.Integer, db.ForeignKey('product_types.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    sku = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    company = relationship("Company", back_populates="products")
    
    # Relationships for bundles
    bundle_of = relationship("Product",
                             secondary=bundle_components,
                             primaryjoin=(bundle_components.c.component_product_id == id),
                             secondaryjoin=(bundle_components.c.bundle_product_id == id),
                             backref="components")

class Inventory(db.Model):
    __tablename__ = 'inventory'
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

class InventoryLog(db.Model):
    __tablename__ = 'inventory_logs'
    id = db.Column(db.BigInteger, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    warehouse_id = db.Column(db.Integer, nullable=False)
    quantity_change = db.Column(db.Integer, nullable=False)
    new_quantity = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(255))
    __table_args__ = (db.ForeignKeyConstraint(['product_id', 'warehouse_id'], ['inventory.product_id', 'inventory.warehouse_id']),)
