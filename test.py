import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import urllib.request

# ========================================
# EV Battery Range Analysis
# Real Data: fueleconomy.gov (EPA)
# ========================================

print("Downloading real EPA data...")
url = "https://www.fueleconomy.gov/feg/epadata/vehicles.csv.zip"
urllib.request.urlretrieve(url, "vehicles.zip")

df_raw = pd.read_csv("vehicles.zip", compression='zip', low_memory=False)

# Sadece elektrikli araçları al
ev = df_raw[df_raw['fuelType1'] == 'Electricity'].copy()

# Gerekli kolonları seç
ev = ev[['make', 'model', 'year', 'range', 'rangeCity', 'rangeHwy', 'city08', 'highway08']].dropna()

print(f"\nToplam {len(ev)} elektrikli araç verisi bulundu!")
print("\nİlk 5 satır:")
print(ev.head())

# Mercedes EQ araçlarını filtrele
mercedes = ev[ev['make'] == 'Mercedes-Benz'].copy()
print(f"\nMercedes-Benz EV sayısı: {len(mercedes)}")
print(mercedes[['model', 'year', 'range']].to_string())

# Grafik 1: Tüm EV markaları menzil karşılaştırması
top_brands = ev.groupby('make')['range'].mean().sort_values(ascending=False).head(15)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('EV Battery Range Analysis\nReal EPA Data - fueleconomy.gov',
             fontsize=14, fontweight='bold')

# Marka bazlı menzil
top_brands.plot(kind='barh', ax=axes[0,0], color='steelblue')
axes[0,0].set_title('Top 15 EV Brands - Avg Range (miles)')
axes[0,0].set_xlabel('Average Range (miles)')
axes[0,0].axvline(x=top_brands.get('Mercedes-Benz', 0), color='red',
                   linestyle='--', label='Mercedes-Benz')
axes[0,0].legend()

# Yıllara göre menzil gelişimi
yearly = ev.groupby('year')['range'].mean()
yearly.plot(ax=axes[0,1], color='darkorange', marker='o')
axes[0,1].set_title('EV Range Improvement Over Years')
axes[0,1].set_xlabel('Year')
axes[0,1].set_ylabel('Average Range (miles)')
axes[0,1].grid(True, alpha=0.3)

# City vs Highway menzil
axes[1,0].scatter(ev['city08'], ev['highway08'], alpha=0.4, color='green')
if len(mercedes) > 0:
    axes[1,0].scatter(mercedes['city08'], mercedes['highway08'],
                      color='red', s=100, zorder=5, label='Mercedes-Benz')
    axes[1,0].legend()
axes[1,0].set_xlabel('City Efficiency (MPGe)')
axes[1,0].set_ylabel('Highway Efficiency (MPGe)')
axes[1,0].set_title('City vs Highway Efficiency')

# Menzil dağılımı
axes[1,1].hist(ev['range'], bins=30, color='purple', alpha=0.7, edgecolor='black')
axes[1,1].set_xlabel('Range (miles)')
axes[1,1].set_ylabel('Number of Vehicles')
axes[1,1].set_title('EV Range Distribution')
if len(mercedes) > 0:
    avg_merc = mercedes['range'].mean()
    axes[1,1].axvline(x=avg_merc, color='red', linestyle='--',
                       label=f'Mercedes avg: {avg_merc:.0f} mi')
    axes[1,1].legend()

plt.tight_layout()
plt.savefig('ev_real_analysis.png', dpi=150)
plt.show()

print("\n✅ Analiz tamamlandı! ev_real_analysis.png kaydedildi.")