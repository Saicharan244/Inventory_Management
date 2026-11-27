
import streamlit as st
import pandas as pd
import plotly.express as px
import json
import time
from pathlib import Path
from datetime import date
from db_connection import get_connection

# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Inventory Management System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# OWNER SETTINGS
# ==================================================

SETTINGS_FILE = Path(__file__).with_name("owner_settings.json")

def load_owner():
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text()).get(
                "owner", "Shop Owner"
            )
        except Exception:
            pass
    return "Shop Owner"

def save_owner(name):
    SETTINGS_FILE.write_text(
        json.dumps({"owner": name}, indent=4)
    )


# ==================================================
# PROFESSIONAL UI DESIGN
# ==================================================

st.markdown("""
<style>
.stApp {
    background: #F4F5EF;
    color: #203B43;
}

.block-container {
    max-width: 1600px;
    padding: 1.3rem 2rem 2rem 2rem;
}

[data-testid="stSidebar"] {
    background: #174E5A;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 12px;
}

[data-testid="stSidebar"] hr {
    border-color: #557984;
}

h1 {
    color: #174E5A !important;
    font-size: 30px !important;
    font-weight: 750 !important;
}

h2, h3 {
    color: #174E5A !important;
}

p, label, span {
    font-size: 14px;
}

.metric-card {
    background: white;
    padding: 19px;
    border-radius: 13px;
    border: 1px solid #E5E8E0;
    min-height: 118px;
    box-shadow: 0 3px 10px rgba(20,50,50,.04);
}

.metric-title {
    color: #73848A;
    font-size: 14px;
    font-weight: 600;
}

.metric-value {
    color: #174E5A;
    font-size: 27px;
    font-weight: 750;
    margin-top: 12px;
}

.panel {
    background: white;
    padding: 18px;
    border-radius: 13px;
    border: 1px solid #E5E8E0;
}

.stButton button {
    background: #F1CB5D;
    color: #203B43;
    border: none;
    border-radius: 8px;
    min-height: 40px;
    font-weight: 650;
}

.stButton button:hover {
    background: #E6BA3E;
    color: #203B43;
}

[data-testid="stDataFrame"] {
    border: 1px solid #E5E8E0;
    border-radius: 10px;
}

[data-testid="stForm"] {
    background: white;
    padding: 18px;
    border: 1px solid #E5E8E0;
    border-radius: 12px;
}

hr {
    border-color: #E1E5DF;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# DATABASE FUNCTIONS
# ==================================================

def load_data(query, params=None):
    conn = get_connection()
    try:
        return pd.read_sql(query, conn, params=params)
    finally:
        conn.close()


def execute_query(query, params=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def metric_card(title, value, icon):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">
            {icon} &nbsp; {title}
        </div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def heading(title, description=None):
    st.subheader(title)
    if description:
        st.caption(description)


# ==================================================
# SESSION STATE
# ==================================================

if "owner" not in st.session_state:
    st.session_state.owner = load_owner()

if "cart" not in st.session_state:
    st.session_state.cart = []

if "last_bill" not in st.session_state:
    st.session_state.last_bill = None


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.markdown("## 📦 INVENTORY")
    st.markdown("### MANAGEMENT SYSTEM")

    st.markdown("---")

    st.markdown("### 👤 SHOP OWNER")

    owner_input = st.text_input(
        "Owner name",
        value=st.session_state.owner
    )

    if st.button("Save Owner Name", use_container_width=True):
        if owner_input.strip():
            st.session_state.owner = owner_input.strip()
            save_owner(owner_input.strip())
            st.success("Owner name saved!")
            st.rerun()

    st.markdown("---")
    st.caption("MAIN MENU")

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Billing",
            "Products",
            "Inventory",
            "Suppliers",
            "Sales History",
            "Reports"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.caption("SHOP MANAGEMENT")
    st.caption("MySQL Database")
    st.caption("Python + Streamlit")


# ==================================================
# MAIN APPLICATION
# ==================================================

try:

    # ==================================================
    # 1. DASHBOARD
    # ==================================================

    if page == "Dashboard":

        st.title("Welcome to Inventory Management 👋")

        st.caption(
            f"Shop Owner: {st.session_state.owner}  |  "
            f"{date.today().strftime('%d %B %Y')}"
        )

        # SUMMARY

        summary = load_data("""
            SELECT
                COUNT(*) AS products,
                COALESCE(SUM(stock),0) AS stock,
                COALESCE(SUM(price * stock),0) AS value
            FROM Products
        """)

        sales = load_data("""
            SELECT
                COALESCE(SUM(total_amount),0) AS revenue,
                COUNT(DISTINCT bill_no) AS bills
            FROM `Orders`
        """)

        low = load_data("""
            SELECT COUNT(*) AS total
            FROM Products
            WHERE stock <= 10
        """)

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            metric_card(
                "TOTAL PRODUCTS",
                f"{int(summary.iloc[0]['products']):,}",
                "📦"
            )

        with c2:
            metric_card(
                "AVAILABLE STOCK",
                f"{int(summary.iloc[0]['stock']):,}",
                "🏬"
            )

        with c3:
            metric_card(
                "TOTAL SALES",
                f"₹{sales.iloc[0]['revenue']:,.0f}",
                "💰"
            )

        with c4:
            metric_card(
                "INVENTORY VALUE",
                f"₹{summary.iloc[0]['value']:,.0f}",
                "📊"
            )

        st.markdown("<br>", unsafe_allow_html=True)

        left, right = st.columns([1.7, 1])

        with left:

            heading(
                "Sales Performance",
                "Monthly sales revenue"
            )

            monthly = load_data("""
                SELECT
                    DATE_FORMAT(order_date,'%Y-%m') AS month,
                    SUM(total_amount) AS revenue
                FROM `Orders`
                GROUP BY month
                ORDER BY month
            """)

            if not monthly.empty:
                fig = px.area(
                    monthly,
                    x="month",
                    y="revenue",
                    markers=True,
                    template="plotly_white",
                    labels={
                        "month": "Month",
                        "revenue": "Revenue (₹)"
                    }
                )

                fig.update_traces(
                    line_color="#159A83",
                    fillcolor="rgba(21,154,131,0.12)"
                )

                fig.update_layout(
                    margin=dict(l=10,r=10,t=20,b=10),
                    height=300
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        with right:

            heading(
                "Inventory Status",
                "Stock by category"
            )

            category = load_data("""
                SELECT
                    c.category_name,
                    SUM(p.stock) AS quantity
                FROM Categories c
                JOIN Products p
                ON c.category_id = p.category_id
                GROUP BY c.category_id,c.category_name
            """)

            if not category.empty:
                fig = px.pie(
                    category,
                    names="category_name",
                    values="quantity",
                    hole=.58,
                    template="plotly_white"
                )

                fig.update_layout(
                    height=300,
                    margin=dict(l=5,r=5,t=20,b=5)
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        st.markdown("---")

        left, right = st.columns(2)

        with left:

            heading("🏆 Top Selling Products")

            top = load_data("""
                SELECT
                    p.product_name,
                    SUM(o.quantity) AS quantity_sold
                FROM `Orders` o
                JOIN Products p
                ON o.product_id = p.product_id
                GROUP BY p.product_id,p.product_name
                ORDER BY quantity_sold DESC
                LIMIT 5
            """)

            if not top.empty:
                fig = px.bar(
                    top,
                    x="quantity_sold",
                    y="product_name",
                    orientation="h",
                    text="quantity_sold",
                    template="plotly_white"
                )

                fig.update_traces(
                    marker_color="#DDBA51",
                    textposition="outside"
                )

                fig.update_layout(
                    height=260,
                    yaxis={"categoryorder": "total ascending"},
                    margin=dict(l=5,r=20,t=15,b=5)
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        with right:

            heading("⚠️ Low Stock Alerts")

            low_products = load_data("""
                SELECT
                    product_name,
                    stock,
                    price
                FROM Products
                WHERE stock <= 10
                ORDER BY stock ASC
            """)

            if not low_products.empty:
                st.dataframe(
                    low_products,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.success("All products have sufficient stock.")

        st.markdown("---")

        heading("Recent Bills")

        recent = load_data("""
            SELECT
                bill_no,
                customer_name,
                COUNT(order_id) AS items,
                SUM(total_amount) AS bill_total,
                MAX(order_date) AS bill_date
            FROM `Orders`
            GROUP BY bill_no, customer_name
            ORDER BY bill_date DESC, bill_no DESC
            LIMIT 5
        """)

        st.dataframe(
            recent,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            f"Total bills recorded: {int(sales.iloc[0]['bills'])} "
            f"| Low-stock products: {int(low.iloc[0]['total'])}"
        )


    # ==================================================
    # 2. BILLING PAGE
    # ==================================================

    elif page == "Billing":

        st.title("🧾 Create New Bill")

        st.caption(
            "Select products, add quantities and generate a customer bill."
        )

        products = load_data("""
            SELECT product_id, product_name, price, stock
            FROM Products
            WHERE stock > 0
            ORDER BY product_name
        """)

        if products.empty:

            st.warning("No products are currently available.")

        else:

            product_options = {
                f"{row.product_name} | ₹{row.price:.2f} | Stock: {row.stock}":
                int(row.product_id)
                for row in products.itertuples()
            }

            customer = st.text_input(
                "Customer Name",
                value="Walk-in Customer"
            )

            st.markdown("---")
            heading("Add Products to Bill")

            selected = st.selectbox(
                "Select Product",
                list(product_options.keys())
            )

            product_id = product_options[selected]

            selected_product = products[
                products["product_id"] == product_id
            ].iloc[0]

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Unit Price",
                    f"₹{selected_product['price']:.2f}"
                )

            with col2:
                st.metric(
                    "Available Stock",
                    int(selected_product["stock"])
                )

            with col3:
                quantity = st.number_input(
                    "Quantity",
                    min_value=1,
                    max_value=int(selected_product["stock"]),
                    value=1,
                    step=1
                )

            if st.button("➕ Add to Bill"):

                existing = next(
                    (
                        item for item in st.session_state.cart
                        if item["product_id"] == product_id
                    ),
                    None
                )

                current_qty = existing["quantity"] if existing else 0

                if current_qty + quantity > int(selected_product["stock"]):
                    st.error("Quantity exceeds available stock.")

                elif existing:
                    existing["quantity"] += int(quantity)
                    st.success("Product quantity updated.")

                else:
                    st.session_state.cart.append({
                        "product_id": product_id,
                        "product_name": selected_product["product_name"],
                        "price": float(selected_product["price"]),
                        "quantity": int(quantity)
                    })

                    st.success("Product added to bill.")

                st.rerun()

            st.markdown("---")
            heading("Current Bill")

            if st.session_state.cart:

                cart_df = pd.DataFrame(st.session_state.cart)

                cart_df["subtotal"] = (
                    cart_df["price"] * cart_df["quantity"]
                )

                st.dataframe(
                    cart_df[
                        ["product_name", "price", "quantity", "subtotal"]
                    ],
                    use_container_width=True,
                    hide_index=True
                )

                total = float(cart_df["subtotal"].sum())

                st.markdown(
                    f"<h2 style='text-align:right;color:#159A83'>"
                    f"Bill Total: ₹{total:,.2f}</h2>",
                    unsafe_allow_html=True
                )

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "🗑 Clear Bill",
                        use_container_width=True
                    ):
                        st.session_state.cart = []
                        st.rerun()

                with col2:

                    if st.button(
                        "✓ Complete Sale",
                        use_container_width=True
                    ):

                        if not customer.strip():
                            st.error("Enter a customer name.")

                        else:

                            conn = get_connection()
                            cursor = conn.cursor()

                            try:

                                conn.start_transaction()

                                # Recheck and lock stock
                                for item in st.session_state.cart:

                                    cursor.execute("""
                                        SELECT stock
                                        FROM Products
                                        WHERE product_id = %s
                                        FOR UPDATE
                                    """, (item["product_id"],))

                                    result = cursor.fetchone()

                                    if (
                                        not result
                                        or result[0] < item["quantity"]
                                    ):
                                        raise ValueError(
                                            f"Insufficient stock for "
                                            f"{item['product_name']}"
                                        )

                                # One bill number for all products
                                bill_no = time.time_ns() // 1000

                                receipt_items = []

                                for item in st.session_state.cart:

                                    subtotal = (
                                        item["price"] * item["quantity"]
                                    )

                                    cursor.execute("""
                                        INSERT INTO `Orders`
                                        (
                                            product_id,
                                            quantity,
                                            order_date,
                                            total_amount,
                                            bill_no,
                                            customer_name
                                        )
                                        VALUES (%s,%s,CURDATE(),%s,%s,%s)
                                    """, (
                                        item["product_id"],
                                        item["quantity"],
                                        subtotal,
                                        bill_no,
                                        customer.strip()
                                    ))

                                    # Deduct product stock
                                    cursor.execute("""
                                        UPDATE Products
                                        SET stock = stock - %s
                                        WHERE product_id = %s
                                    """, (
                                        item["quantity"],
                                        item["product_id"]
                                    ))

                                    # Synchronize stock table
                                    cursor.execute("""
                                        UPDATE Stock
                                        SET quantity_available =
                                            quantity_available - %s,
                                            last_updated = CURDATE()
                                        WHERE product_id = %s
                                    """, (
                                        item["quantity"],
                                        item["product_id"]
                                    ))

                                    receipt_items.append({
                                        **item,
                                        "subtotal": subtotal
                                    })

                                conn.commit()

                                st.session_state.last_bill = {
                                    "bill_no": bill_no,
                                    "customer": customer.strip(),
                                    "items": receipt_items,
                                    "total": total,
                                    "date": date.today().strftime(
                                        "%d-%m-%Y"
                                    )
                                }

                                st.session_state.cart = []

                                st.success(
                                    f"Bill #{bill_no} generated successfully!"
                                )

                            except Exception as e:

                                conn.rollback()
                                st.error(f"Sale failed: {e}")

                            finally:
                                cursor.close()
                                conn.close()

                            st.rerun()

            else:
                st.info("Your bill is empty. Add products to continue.")

        # RECEIPT

        if st.session_state.last_bill:

            bill = st.session_state.last_bill

            st.markdown("---")
            heading("Latest Bill Receipt")

            st.markdown(f"""
            <div class="panel">
                <h2>🧾 {st.session_state.owner}</h2>
                <p>INVENTORY MANAGEMENT SYSTEM</p>
                <hr>
                <b>Bill Number:</b> {bill['bill_no']}<br>
                <b>Customer:</b> {bill['customer']}<br>
                <b>Date:</b> {bill['date']}<br>
                <hr>
            </div>
            """, unsafe_allow_html=True)

            receipt_df = pd.DataFrame(bill["items"])

            st.dataframe(
                receipt_df[
                    ["product_name", "price", "quantity", "subtotal"]
                ],
                use_container_width=True,
                hide_index=True
            )

            st.success(f"TOTAL AMOUNT: ₹{bill['total']:,.2f}")

            receipt_text = (
                f"{st.session_state.owner}\n"
                f"INVENTORY MANAGEMENT SYSTEM\n"
                f"Bill No: {bill['bill_no']}\n"
                f"Customer: {bill['customer']}\n"
                f"Date: {bill['date']}\n\n"
            )

            for item in bill["items"]:
                receipt_text += (
                    f"{item['product_name']} | "
                    f"{item['quantity']} x "
                    f"₹{item['price']:.2f} = "
                    f"₹{item['subtotal']:.2f}\n"
                )

            receipt_text += (
                f"\nTOTAL: ₹{bill['total']:.2f}\n"
            )

            st.download_button(
                "⬇ Download Bill Receipt",
                receipt_text,
                file_name=f"Bill_{bill['bill_no']}.txt",
                mime="text/plain"
            )


    # ==================================================
    # 3. PRODUCT MANAGEMENT
    # ==================================================

    elif page == "Products":

        st.title("📦 Product Management")

        tab1, tab2, tab3 = st.tabs([
            "All Products",
            "Add Product",
            "Edit / Delete"
        ])

        with tab1:

            products = load_data("""
                SELECT
                    p.product_id,
                    p.product_name,
                    c.category_name,
                    s.supplier_name,
                    p.price,
                    p.stock
                FROM Products p
                JOIN Categories c
                ON p.category_id = c.category_id
                JOIN Suppliers s
                ON p.supplier_id = s.supplier_id
                ORDER BY p.product_id
            """)

            search = st.text_input(
                "Search product",
                placeholder="Product name..."
            )

            if search:
                products = products[
                    products["product_name"].str.contains(
                        search, case=False, na=False
                    )
                ]

            st.dataframe(
                products,
                use_container_width=True,
                hide_index=True
            )

            st.metric("Products", len(products))

        with tab2:

            heading("Register New Product")

            categories = load_data("""
                SELECT category_id, category_name FROM Categories
            """)

            suppliers = load_data("""
                SELECT supplier_id, supplier_name FROM Suppliers
            """)

            with st.form("add_product_form"):

                name = st.text_input("Product Name")
                price = st.number_input(
                    "Price",
                    min_value=0.01,
                    value=100.0
                )

                category_map = dict(zip(
                    categories["category_name"],
                    categories["category_id"]
                ))

                supplier_map = dict(zip(
                    suppliers["supplier_name"],
                    suppliers["supplier_id"]
                ))

                category_name = st.selectbox(
                    "Category",
                    list(category_map.keys())
                )

                supplier_name = st.selectbox(
                    "Supplier",
                    list(supplier_map.keys())
                )

                stock_qty = st.number_input(
                    "Opening Stock",
                    min_value=0,
                    value=10
                )

                submit = st.form_submit_button(
                    "Add Product",
                    use_container_width=True
                )

                if submit:

                    if not name.strip():
                        st.error("Enter a product name.")

                    else:

                        conn = get_connection()
                        cursor = conn.cursor()

                        try:

                            conn.start_transaction()

                            cursor.execute("""
                                INSERT INTO Products
                                (product_name,price,category_id,
                                 supplier_id,stock)
                                VALUES (%s,%s,%s,%s,%s)
                            """, (
                                name.strip(),
                                price,
                                category_map[category_name],
                                supplier_map[supplier_name],
                                stock_qty
                            ))

                            new_id = cursor.lastrowid

                            cursor.execute("""
                                INSERT INTO Stock
                                (product_id,quantity_available,last_updated)
                                VALUES (%s,%s,CURDATE())
                            """, (new_id, stock_qty))

                            conn.commit()
                            st.success("Product added successfully!")

                        except Exception as e:
                            conn.rollback()
                            st.error(str(e))

                        finally:
                            cursor.close()
                            conn.close()

        with tab3:

            heading("Edit or Delete Product")

            products = load_data("""
                SELECT product_id, product_name, price, stock
                FROM Products
                ORDER BY product_id
            """)

            if not products.empty:

                product_map = {
                    f"{r.product_name} (ID: {r.product_id})":
                    int(r.product_id)
                    for r in products.itertuples()
                }

                selected = st.selectbox(
                    "Choose Product",
                    list(product_map.keys())
                )

                pid = product_map[selected]

                product = products[
                    products["product_id"] == pid
                ].iloc[0]

                st.markdown("---")

                with st.form("edit_product_form"):

                    new_name = st.text_input(
                        "Product Name",
                        value=product["product_name"]
                    )

                    new_price = st.number_input(
                        "Price",
                        min_value=0.01,
                        value=float(product["price"])
                    )

                    update = st.form_submit_button(
                        "Save Changes",
                        use_container_width=True
                    )

                    if update:

                        if not new_name.strip():
                            st.error("Product name cannot be empty.")
                        else:
                            execute_query("""
                                UPDATE Products
                                SET product_name=%s, price=%s
                                WHERE product_id=%s
                            """, (new_name.strip(), new_price, pid))

                            st.success("Product updated!")
                            st.rerun()

                st.markdown("---")

                if st.button(
                    "🗑 Delete Selected Product",
                    use_container_width=True
                ):

                    conn = get_connection()
                    cursor = conn.cursor()

                    try:

                        cursor.execute("""
                            SELECT COUNT(*)
                            FROM `Orders`
                            WHERE product_id=%s
                        """, (pid,))

                        history = cursor.fetchone()[0]

                        if history > 0:

                            st.error(
                                "Cannot delete this product because "
                                "it has sales history. Preserve the "
                                "historical records."
                            )

                        else:

                            conn.start_transaction()

                            cursor.execute("""
                                DELETE FROM Stock
                                WHERE product_id=%s
                            """, (pid,))

                            cursor.execute("""
                                DELETE FROM Products
                                WHERE product_id=%s
                            """, (pid,))

                            conn.commit()

                            st.success("Product deleted successfully!")
                            st.rerun()

                    except Exception as e:
                        conn.rollback()
                        st.error(str(e))

                    finally:
                        cursor.close()
                        conn.close()


    # ==================================================
    # 4. INVENTORY MANAGEMENT
    # ==================================================

    elif page == "Inventory":

        st.title("🏬 Inventory Management")

        stock = load_data("""
            SELECT
                p.product_id,
                p.product_name,
                p.price,
                p.stock,
                st.quantity_available,
                p.price*p.stock AS inventory_value
            FROM Products p
            JOIN Stock st
            ON p.product_id=st.product_id
            ORDER BY p.stock ASC
        """)

        c1, c2 = st.columns(2)

        c1.metric(
            "Total Units",
            int(stock["stock"].sum())
        )

        c2.metric(
            "Inventory Value",
            f"₹{stock['inventory_value'].sum():,.2f}"
        )

        heading("Current Stock Details")

        st.dataframe(
            stock,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        heading("Update Stock Quantity")

        product_map = {
            f"{r.product_name} (ID: {r.product_id})":
            int(r.product_id)
            for r in stock.itertuples()
        }

        selected = st.selectbox(
            "Select product",
            list(product_map.keys())
        )

        pid = product_map[selected]

        current = stock[
            stock["product_id"] == pid
        ].iloc[0]

        with st.form("update_stock_form"):

            st.write(
                f"Current quantity: {int(current['stock'])}"
            )

            new_stock = st.number_input(
                "New available quantity",
                min_value=0,
                value=int(current["stock"])
            )

            update_stock = st.form_submit_button(
                "Update Inventory",
                use_container_width=True
            )

            if update_stock:

                conn = get_connection()
                cursor = conn.cursor()

                try:

                    conn.start_transaction()

                    cursor.execute("""
                        UPDATE Products
                        SET stock=%s
                        WHERE product_id=%s
                    """, (new_stock, pid))

                    cursor.execute("""
                        UPDATE Stock
                        SET quantity_available=%s,
                            last_updated=CURDATE()
                        WHERE product_id=%s
                    """, (new_stock, pid))

                    conn.commit()

                    st.success("Stock updated successfully!")
                    st.rerun()

                except Exception as e:
                    conn.rollback()
                    st.error(str(e))

                finally:
                    cursor.close()
                    conn.close()


    # ==================================================
    # 5. SUPPLIERS
    # ==================================================

    elif page == "Suppliers":

        st.title("Supplier Management")

        suppliers = load_data("""
            SELECT * FROM Suppliers
            ORDER BY supplier_id
        """)

        st.dataframe(
            suppliers,
            use_container_width=True,
            hide_index=True
        )

        heading("Supplier Performance")

        performance = load_data("""
            SELECT
                s.supplier_name,
                COUNT(o.order_id) AS total_orders,
                SUM(o.quantity) AS units_sold,
                SUM(o.total_amount) AS revenue
            FROM Suppliers s
            JOIN Products p
            ON s.supplier_id=p.supplier_id
            JOIN `Orders` o
            ON p.product_id=o.product_id
            GROUP BY s.supplier_id,s.supplier_name
            ORDER BY units_sold DESC
        """)

        st.dataframe(
            performance,
            use_container_width=True,
            hide_index=True
        )


    # ==================================================
    # 6. SALES HISTORY
    # ==================================================

    elif page == "Sales History":

        st.title("Sales History")

        bills = load_data("""
            SELECT
                bill_no,
                customer_name,
                COUNT(order_id) AS items,
                SUM(quantity) AS units,
                SUM(total_amount) AS total,
                MAX(order_date) AS bill_date
            FROM `Orders`
            GROUP BY bill_no,customer_name
            ORDER BY bill_date DESC,bill_no DESC
        """)

        st.metric("Total Bills", len(bills))

        st.dataframe(
            bills,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        heading("View Bill Details")

        if not bills.empty:

            selected_bill = st.selectbox(
                "Select Bill Number",
                bills["bill_no"].tolist()
            )

            details = load_data("""
                SELECT
                    p.product_name,
                    o.quantity,
                    p.price,
                    o.total_amount
                FROM `Orders` o
                JOIN Products p
                ON o.product_id=p.product_id
                WHERE o.bill_no=%s
            """, params=(selected_bill,))

            st.dataframe(
                details,
                use_container_width=True,
                hide_index=True
            )

            st.success(
                f"Bill Total: ₹{details['total_amount'].sum():,.2f}"
            )


    # ==================================================
    # 7. REPORTS
    # ==================================================

    elif page == "Reports":

        st.title("Business Reports")

        report = st.selectbox(
            "Choose Report",
            [
                "Top 5 Most Sold Products",
                "Most Active Suppliers",
                "Monthly Sales",
                "Highest Revenue Product",
                "Inventory Value Analysis",
                "Low Stock Report"
            ]
        )

        queries = {

            "Top 5 Most Sold Products": """
                SELECT p.product_name,
                       SUM(o.quantity) AS total_sold
                FROM `Orders` o
                JOIN Products p ON o.product_id=p.product_id
                GROUP BY p.product_id,p.product_name
                ORDER BY total_sold DESC LIMIT 5
            """,

            "Most Active Suppliers": """
                SELECT s.supplier_name,
                       COUNT(o.order_id) AS total_orders,
                       SUM(o.quantity) AS units_sold,
                       SUM(o.total_amount) AS sales
                FROM Suppliers s
                JOIN Products p ON s.supplier_id=p.supplier_id
                JOIN `Orders` o ON p.product_id=o.product_id
                GROUP BY s.supplier_id,s.supplier_name
                ORDER BY units_sold DESC
            """,

            "Monthly Sales": """
                SELECT DATE_FORMAT(order_date,'%Y-%m') AS month,
                       COUNT(*) AS orders,
                       SUM(total_amount) AS revenue
                FROM `Orders`
                GROUP BY month ORDER BY month
            """,

            "Highest Revenue Product": """
                SELECT p.product_name,
                       SUM(o.total_amount) AS revenue
                FROM Products p
                JOIN `Orders` o ON p.product_id=o.product_id
                GROUP BY p.product_id,p.product_name
                ORDER BY revenue DESC LIMIT 1
            """,

            "Inventory Value Analysis": """
                SELECT c.category_name,
                       COUNT(p.product_id) AS products,
                       SUM(p.stock) AS units,
                       SUM(p.price*p.stock) AS inventory_value
                FROM Categories c
                JOIN Products p ON c.category_id=p.category_id
                GROUP BY c.category_id,c.category_name
            """,

            "Low Stock Report": """
                SELECT p.product_name,
                       p.stock,
                       s.supplier_name
                FROM Products p
                JOIN Suppliers s ON p.supplier_id=s.supplier_id
                WHERE p.stock<=10
                ORDER BY p.stock
            """
        }

        result = load_data(queries[report])

        st.subheader(report)

        st.dataframe(
            result,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "⬇ Download CSV",
            data=result.to_csv(index=False).encode("utf-8"),
            file_name="inventory_report.csv",
            mime="text/csv"
        )


except Exception as e:

    st.error("Application Error")
    st.exception(e)
