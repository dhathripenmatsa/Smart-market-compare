import streamlit as st
import pandas as pd

# ---------- Helpers ----------

def load_data():
    return pd.read_csv("prices.csv")

def load_html(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_css(path):
    with open(path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def format_price(val):
    return f"₹{val:.2f}" if pd.notnull(val) else "-"

def highlight_price(val, min_val):
    return 'background-color: #d1ffd1' if val == min_val else ''

def highlight_total(val):
    min_val = min(val)
    return ['background-color: #d1ffd1' if v == min_val else '' for v in val]

# ---------- App ----------

def main():
    st.set_page_config(page_title="Smart Market Compare", layout="wide")

    # Load styles and banner
    load_css("style.css")
    st.markdown(load_html("header.html"), unsafe_allow_html=True)

    df = load_data()

    # Sidebar filters
    st.sidebar.header("🔎 Filter Options")
    selected_stores = st.sidebar.multiselect(
        "Select store(s):", options=df["store"].unique(), default=list(df["store"].unique())
    )

    item_query = st.text_input("🔍 Enter item name (e.g., Milk, Soap):")

    df_filtered = df[df["store"].isin(selected_stores)]

    # ---------- Search ----------
    if item_query:
        df_search = df_filtered[df_filtered["item"].str.contains(item_query, case=False, na=False)]

        if df_search.empty:
            st.warning("No items found for that search.")
        else:
            st.subheader(f"📦 Search Results for: `{item_query}`")
            best_price = df_search["price"].min()
            best_store = df_search[df_search["price"] == best_price]["store"].values[0]

            st.markdown(f"""
                <div style="padding:10px; background-color:#e0ffe0; border-left:6px solid #34a853;">
                    💰 <b>Lowest price for</b> <i>{item_query}</i>: <b>₹{best_price:.2f}</b> <br>
                    🏪 <span style="background-color:#34a853; color:white; padding:4px 10px; border-radius:5px;">{best_store}</span>
                </div>
            """, unsafe_allow_html=True)

            st.dataframe(
                df_search.style.applymap(lambda val: highlight_price(val, best_price), subset=["price"]),
                use_container_width=True
            )

    # ---------- Cart ----------
    st.markdown("---")
    st.subheader("🛒 Build Your Cart and Compare Store Totals")

    all_items = sorted(df["item"].unique())
    selected_items = st.multiselect("Select items to add to cart:", all_items)

    item_quantities = {}

    if selected_items:
        st.markdown("### 🧮 Set Quantities for Selected Items:")
        for item in selected_items:
            qty = st.number_input(f"{item} Quantity", min_value=1, max_value=100, value=1, step=1, key=f"qty_{item}")
            item_quantities[item] = qty

        cart_df = df_filtered[df_filtered["item"].isin(selected_items)]
        pivot = cart_df.pivot_table(index="store", columns="item", values="price", aggfunc="min")

        for item, qty in item_quantities.items():
            if item in pivot.columns:
                pivot[item] = pivot[item] * qty

        pivot["Total"] = pivot.sum(axis=1)
        formatted_pivot = pivot.applymap(lambda x: f"₹{x:.2f}" if pd.notnull(x) else "-")

        st.dataframe(
            formatted_pivot.style.apply(highlight_total, axis=0, subset=["Total"]),
            use_container_width=True
        )

        best_store = pivot["Total"].idxmin()
        min_total = pivot["Total"].min()

        st.markdown(f"""
            <div style="padding:10px; background-color:#e0ffe0; border-left:6px solid #34a853;">
                ✅ <b>Best total price:</b> ₹{min_total:.2f} <br>
                🏪 <span style="background-color:#34a853; color:white; padding:4px 10px; border-radius:5px;">{best_store}</span>
            </div>
        """, unsafe_allow_html=True)

    else:
        st.info("Select items above to build your cart.")

if __name__ == "__main__":
    main()

