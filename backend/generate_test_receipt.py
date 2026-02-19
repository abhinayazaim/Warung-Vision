from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A6
from reportlab.lib import colors
import random
import os
from datetime import datetime, timedelta
from typing import Any

# Create output directory
output_dir = "batch_test_data"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Item Database (Base Prices)
ITEMS_DB = {
    "Beras (5kg)": 65000,
    "Minyak Goreng (2L)": 35000,
    "Gula Pasir (1kg)": 16000,
    "Telur Ayam (1kg)": 28000,
    "Mie Instan (Dus)": 110000,
    "Kopi Kapal Api": 15000,
    "Sabun Mandi (3pcs)": 12000,
    "Sampo Lifebuoy": 22000,
    "Teh Celup Sariwangi": 8500,
    "Tepung Terigu": 11000
}

def generate_receipt(receipt_id):
    # 1. Randomize Financials
    # Pick 3-6 items
    num_items = random.randint(3, 6)
    selected_items = random.sample(list(ITEMS_DB.keys()), num_items)
    
    
    transaction_items: list[dict[str, Any]] = []
    total_amount = 0
    
    for item_name in selected_items:
        base_price = ITEMS_DB[item_name]
        
        # Price Fluctuation (+/- 10%)
        fluctuation = random.uniform(0.9, 1.1)
        price = int(base_price * fluctuation / 500) * 500 # Round to nearest 500
        
        # Quantity (1-3)
        qty = random.randint(1, 3)
        
        subtotal = price * qty
        total_amount += subtotal
        
        transaction_items.append({
            "name": str(item_name),
            "qty": qty,
            "price": price,
            "subtotal": subtotal
        })
        
    # 2. Randomize Date (Last 14 days)
    days_ago = random.randint(0, 14)
    tx_date = datetime.now() - timedelta(days=days_ago)
    date_str = tx_date.strftime("%Y-%m-%d")
    time_str = tx_date.strftime("%H:%M")
    
    # 3. Meta Data
    random_digits = random.randint(100, 999)
    nota_no = f"NJ-{tx_date.strftime('%Y%m%d')}-{random_digits}"
    
    # 4. Generate PDF
    filename = f"{output_dir}/test_receipt_{receipt_id}.pdf"
    c = canvas.Canvas(filename, pagesize=A6)
    width, height = A6
    
    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 30, "WARUNG BERKAH")
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, height - 45, "Jl. Raya Example No. 123")
    c.drawCentredString(width/2, height - 55, "Telp: 0812-3456-7890")
    
    c.line(10, height - 65, width - 10, height - 65)
    
    # Meta
    c.setFont("Helvetica", 9)
    c.drawString(10, height - 80, f"No. Nota: {nota_no}")
    c.drawString(10, height - 95, f"Tanggal : {date_str} {time_str}")
    
    # Table Header
    y = height - 120
    c.setFont("Helvetica-Bold", 9)
    c.drawString(10, y, "Item")
    c.drawString(150, y, "Qty")
    c.drawString(180, y, "Total")
    
    y -= 15
    c.setFont("Helvetica", 9)
    
    # Items
    for item in transaction_items:
        c.drawString(10, y, item['name'][:20]) # Truncate if too long (simple logic)
        c.drawString(155, y, str(item['qty']))
        c.drawString(180, y, f"{item['subtotal']:,}")
        y -= 15
        
    c.line(10, y, width - 10, y)
    y -= 15
    
    # Total
    c.setFont("Helvetica-Bold", 11)
    c.drawString(100, y, "TOTAL:")
    c.drawString(180, y, f"Rp {total_amount:,}")
    
    c.save()
    print(f"Generated: {filename} (Date: {date_str}, Total: Rp {total_amount:,})")

def main():
    print("Generating batch test receipts...")
    for i in range(1, 11):
        generate_receipt(i)
    print("Done!")

if __name__ == "__main__":
    main()
