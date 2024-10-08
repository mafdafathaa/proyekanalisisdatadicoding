import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import urllib
import matplotlib.image as mpimg

# Set up the Streamlit page layout
st.set_page_config(page_title="Dashboard E-commerce", layout="wide")

# Load the dataset
@st.cache
def load_data():
    all_data = pd.read_csv('all_data.csv', parse_dates=['order_purchase_timestamp'])
    geolocation = pd.read_csv('geolocation.csv')  # Load geolocation data
    return all_data, geolocation

# Load data
all_data, geolocation = load_data()

# Dashboard title
st.title("Dashboard E-commerce - Analisis Produk dan Customer")

# 1. Produk Terlaris dan Paling Sedikit Terjual
st.write("## 5 Produk Terlaris Berdasarkan Kategori")
top_products = all_data.groupby('product_category_name_english')['order_id'].count().sort_values(ascending=False).head(5)
fig1, ax1 = plt.subplots(figsize=(10, 5))
sns.barplot(x=top_products.index, y=top_products.values, ax=ax1, palette="viridis") 
ax1.set_title('5 Produk Terlaris Berdasarkan Kategori')
ax1.set_xlabel('Kategori Produk')
ax1.set_ylabel('Jumlah Order')
plt.xticks(rotation=45, ha='right')
st.pyplot(fig1)

st.write("## 5 Produk Paling Sedikit Terjual Berdasarkan Kategori")
bottom_products = all_data.groupby('product_category_name_english')['order_id'].count().sort_values(ascending=True).head(5)
fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.barplot(x=bottom_products.index, y=bottom_products.values, ax=ax2, palette="viridis") 
ax2.set_title('5 Produk Paling Sedikit Terjual Berdasarkan Kategori')
ax2.set_xlabel('Kategori Produk')
ax2.set_ylabel('Jumlah Order')
plt.xticks(rotation=45, ha='right')
st.pyplot(fig2)

# 2. Analisis Geolokasi Pelanggan dan Peta Brasil
st.write("## Analisis Geolokasi Sebaran  Pelanggan")

# Menyiapkan geolocation data
if 'geolocation_zip_code_prefix' in geolocation.columns:
    geolocation_silver = geolocation.groupby(['geolocation_zip_code_prefix', 'geolocation_city', 'geolocation_state'])[['geolocation_lat', 'geolocation_lng']].median().reset_index()

    # Merging geolocation with all_data (assuming you have a customer_zip_code_prefix in all_data)
    all_data = all_data.rename(columns={'customer_zip_code_prefix': 'geolocation_zip_code_prefix'})
    customers_silver = all_data.merge(geolocation_silver, on='geolocation_zip_code_prefix', how='inner')
    
    if not customers_silver.empty:
        # Fungsi untuk memplot peta Brasil
        def plot_brazil_map(data):
            url = 'https://i.pinimg.com/originals/3a/0c/e1/3a0ce18b3c842748c255bc0aa445ad41.jpg'
            brazil = mpimg.imread(urllib.request.urlopen(url), 'jpg')
            fig, ax = plt.subplots(figsize=(10, 10))
            data.plot(kind="scatter", x="geolocation_lng", y="geolocation_lat", figsize=(10, 10), alpha=0.3, s=0.3, c='maroon', ax=ax)
            plt.axis('off')
            plt.imshow(brazil, extent=[-73.98283055, -33.8, -33.75116944, 5.4])
            plt.title("Distribusi Pelanggan di Brasil")
            st.pyplot(fig)

        unique_customers = customers_silver.drop_duplicates(subset='customer_unique_id')
        plot_brazil_map(unique_customers)
    else:
        st.write("Data pelanggan kosong setelah penggabungan dengan geolocation.")
else:
    st.write("Kolom geolocation_zip_code_prefix tidak ditemukan dalam geolocation.csv.")

# 3. Analisis Pola Pembelian dalam 6 Bulan Terakhir
st.write("## Pola Pembelian Customer dalam 6 Bulan Terakhir")
six_months_ago = all_data['order_purchase_timestamp'].max() - pd.DateOffset(months=6)
recent_orders = all_data[all_data['order_purchase_timestamp'] >= six_months_ago]

# Analisis pola pembelian berdasarkan bulan
monthly_orders = recent_orders.groupby(recent_orders['order_purchase_timestamp'].dt.month)['order_id'].count()
fig3, ax3 = plt.subplots(figsize=(10, 5))
sns.lineplot(x=monthly_orders.index, y=monthly_orders.values, ax=ax3, color="red")
ax3.set_title('Pola Pembelian Customer dalam 6 Bulan Terakhir')
ax3.set_xlabel('Bulan')
ax3.set_ylabel('Jumlah Order')
st.pyplot(fig3)

# Analisis pola pembelian berdasarkan hari dalam seminggu
weekly_orders = recent_orders.groupby(recent_orders['order_purchase_timestamp'].dt.dayofweek)['order_id'].count()
fig4, ax4 = plt.subplots(figsize=(10, 5))
sns.barplot(x=weekly_orders.index, y=weekly_orders.values, ax=ax4, palette="coolwarm") 
ax4.set_title('Pola Pembelian Customer Berdasarkan Hari dalam Seminggu (6 Bulan Terakhir)')
ax4.set_xlabel('Hari dalam Seminggu (0=Senin, 6=Minggu)')
ax4.set_ylabel('Jumlah Order')
st.pyplot(fig4)
