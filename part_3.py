from flask import Flask, jsonify, request
from datetime import datetime, timedelta
from models import db, Company, Warehouse, Product, Inventory, Supplier, Sales

app = Flask(__name__)

@app.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def get_low_stock_alerts(company_id):
    try:
        # Get all warehouses for this company
        warehouses = Warehouse.query.filter_by(company_id=company_id).all()
        if not warehouses:
            return jsonify({"message": "No warehouses found for this company"}), 404
        
        warehouse_ids = [w.id for w in warehouses]
        
        # Get inventory items for these warehouses
        inventories = Inventory.query.filter(Inventory.warehouse_id.in_(warehouse_ids)).all()
        alerts = []
        
        for inv in inventories:
            # Skip if product not found
            product = Product.query.get(inv.product_id)
            if not product:
                continue
            
            # Check recent sales (within last 30 days)
            recent_sales = Sales.query.filter(
                Sales.product_id == product.id,
                Sales.date >= datetime.now() - timedelta(days=30)
            ).count()
            
            if recent_sales == 0:
                continue  # skip inactive products
            
            # Check low stock condition
            if inv.quantity <= inv.threshold:
                supplier = Supplier.query.get(product.supplier_id)
                warehouse = Warehouse.query.get(inv.warehouse_id)
                
                alert = {
                    "product_id": product.id,
                    "product_name": product.name,
                    "sku": product.sku,
                    "warehouse_id": warehouse.id,
                    "warehouse_name": warehouse.name,
                    "current_stock": inv.quantity,
                    "threshold": inv.threshold,
                    "days_until_stockout": 10,  # sample estimate
                    "supplier": {
                        "id": supplier.id,
                        "name": supplier.name,
                        "contact_email": supplier.contact_email
                    } if supplier else None
                }
                alerts.append(alert)
        
        return jsonify({
            "alerts": alerts,
            "total_alerts": len(alerts)
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500