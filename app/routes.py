from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, case
from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta

from app import app, db
from app.models import Product, Inventory, Company, Warehouse, Supplier, ProductType, InventoryLog

@app.route('/api/products', methods=['POST'])
def create_product():
    """
    Creates a new product and adds its initial inventory to a specified warehouse.
    This is a transactional operation; it either fully succeeds or fails without side effects.
    """
    data = request.json
    if not data:
        return jsonify({"error": "Invalid request. JSON body is required."}), 400

    required_fields = ['name', 'sku', 'price', 'warehouse_id', 'initial_quantity']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    if Product.query.filter_by(sku=data['sku']).first():
        return jsonify({"error": f"Product with SKU '{data['sku']}' already exists."}), 409

    try:
        new_product = Product(
            name=data['name'],
            sku=data['sku'],
            price=Decimal(data['price'])
        )
        db.session.add(new_product)
        db.session.flush()

        new_inventory = Inventory(
            product_id=new_product.id,
            warehouse_id=data['warehouse_id'],
            quantity=int(data['initial_quantity'])
        )
        db.session.add(new_inventory)
        db.session.commit()

        return jsonify({
            "message": "Product and initial inventory created successfully.",
            "product": {"id": new_product.id, "name": new_product.name, "sku": new_product.sku}
        }), 201

    except (InvalidOperation, ValueError):
        db.session.rollback()
        return jsonify({"error": "Invalid data type for price or quantity."}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database integrity error. Does the warehouse exist?"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred."}), 500


@app.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def get_low_stock_alerts(company_id):
    """
    Returns a list of products that are below their defined stock threshold
    and have had recent sales activity for a given company.
    """
    if not Company.query.get(company_id):
        return jsonify({"error": "Company not found"}), 404

    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    sales_subquery = db.session.query(
        InventoryLog.product_id,
        func.sum(case([(InventoryLog.quantity_change < 0, -InventoryLog.quantity_change)], else_=0)).label('total_sold_30d')
    ).filter(
        InventoryLog.created_at >= thirty_days_ago,
        InventoryLog.reason.like('%sale%')
    ).group_by(InventoryLog.product_id).subquery()

    query_results = db.session.query(
        Product.id.label('product_id'), Product.name.label('product_name'), Product.sku,
        Warehouse.id.label('warehouse_id'), Warehouse.name.label('warehouse_name'),
        Inventory.quantity.label('current_stock'), ProductType.low_stock_threshold.label('threshold'),
        Supplier.id.label('supplier_id'), Supplier.name.label('supplier_name'), Supplier.contact_email.label('supplier_contact_email'),
        sales_subquery.c.total_sold_30d
    ).join(Inventory, Product.id == Inventory.product_id) \
     .join(Warehouse, Inventory.warehouse_id == Warehouse.id) \
     .join(ProductType, Product.product_type_id == ProductType.id) \
     .outerjoin(Supplier, Product.supplier_id == Supplier.id) \
     .outerjoin(sales_subquery, Product.id == sales_subquery.c.product_id) \
     .filter(
        Warehouse.company_id == company_id,
        Inventory.quantity <= ProductType.low_stock_threshold,
        sales_subquery.c.total_sold_30d > 0
    ).all()

    alerts = []
    for row in query_results:
        avg_daily_sales = (row.total_sold_30d or 0) / 30.0
        days_until_stockout = int(row.current_stock / avg_daily_sales) if avg_daily_sales > 0 else None
        alerts.append({
            "product_id": row.product_id, "product_name": row.product_name, "sku": row.sku,
            "warehouse_id": row.warehouse_id, "warehouse_name": row.warehouse_name,
            "current_stock": row.current_stock, "threshold": row.threshold,
            "days_until_stockout": days_until_stockout,
            "supplier": {"id": row.supplier_id, "name": row.supplier_name, "contact_email": row.supplier_contact_email} if row.supplier_id else None
        })

    return jsonify({"alerts": alerts, "total_alerts": len(alerts)})
