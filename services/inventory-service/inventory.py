import logging
import psycopg2
from config import DATABASE_URL, SERVICE_NAME

logger = logging.getLogger(SERVICE_NAME)


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    """Create inventory table and seed sample products if empty."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            product_id VARCHAR(50) PRIMARY KEY,
            product_name VARCHAR(255) NOT NULL,
            stock INT NOT NULL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)
    cur.execute("SELECT COUNT(*) FROM inventory")
    count = cur.fetchone()[0]
    if count == 0:
        logger.info("Seeding inventory with sample products...")
        cur.executemany(
            "INSERT INTO inventory (product_id, product_name, stock) VALUES (%s, %s, %s)",
            [
                ("PROD10", "Wireless Headphones", 100),
                ("PROD20", "Mechanical Keyboard", 50),
                ("PROD30", "USB-C Hub", 200),
                ("PROD40", "Monitor Stand", 75),
                ("PROD50", "Webcam HD", 150),
            ],
        )
    conn.commit()
    cur.close()
    conn.close()
    logger.info("Inventory DB initialized")


def reduce_stock(product_id: str, quantity: int) -> dict:
    """Reduce stock for a product. Returns updated inventory info."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT stock FROM inventory WHERE product_id = %s FOR UPDATE", (product_id,))
    row = cur.fetchone()

    if row is None:
        cur.close()
        conn.close()
        logger.warning(f"Product {product_id} not found in inventory")
        return {"product_id": product_id, "status": "PRODUCT_NOT_FOUND"}

    current_stock = row[0]

    if current_stock < quantity:
        cur.close()
        conn.close()
        logger.warning(f"Insufficient stock for {product_id}: have={current_stock}, need={quantity}")
        return {
            "product_id": product_id,
            "status": "OUT_OF_STOCK",
            "available": current_stock,
            "requested": quantity,
        }

    new_stock = current_stock - quantity
    cur.execute(
        "UPDATE inventory SET stock = %s, updated_at = NOW() WHERE product_id = %s",
        (new_stock, product_id),
    )
    conn.commit()
    cur.close()
    conn.close()

    logger.info(f"Stock updated: {product_id} {current_stock} → {new_stock}")
    return {
        "product_id": product_id,
        "status": "STOCK_UPDATED",
        "previous_stock": current_stock,
        "new_stock": new_stock,
        "quantity_deducted": quantity,
    }
