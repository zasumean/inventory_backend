from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from decimal import Decimal

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()

    # Input Validation
    required_fields = ['name', 'sku', 'price', 'warehouse_id', 'initial_quantity']
    missing = [field for field in required_fields if field not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    # Type Validation
    try:
        price = Decimal(str(data['price']))  # avoids float rounding issues
        warehouse_id = int(data['warehouse_id'])
        quantity = int(data['initial_quantity'])
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid data type for price, warehouse_id, or quantity"}), 400

    # Check for duplicate sku
    existing_product = Product.query.filter_by(sku=data['sku']).first()
    if existing_product:
        return jsonify({"error": "SKU already exists"}), 409

    try:
        # Create Product
        product = Product(
            name=data.get('name'),
            sku=data.get('sku'),
            price=price 
            supplier_id=supplier_id
            
        )

        db.session.add(product)
        db.session.flush()  # ensures product.id is available before inventory creation

        # inventory save
        inventory = Inventory(
            product_id=product.id,
            warehouse_id=warehouse_id,
            quantity=quantity
        )
        db.session.add(inventory)

        # One commit for both product and inventory saves.
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database integrity error"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    # response
    return jsonify({
        "message": "Product created successfully",
        "product_id": product.id
    }), 201
