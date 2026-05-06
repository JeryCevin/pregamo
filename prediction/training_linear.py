# prediction/training_linear.py
"""
Modul untuk training model Linear Regression dengan Pipeline.
Format features: year, mileage, engineSize, model, transmission, fuelType.
"""

import os
import pandas as pd
import joblib
from datetime import datetime
from django.conf import settings
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, mean_absolute_percentage_error
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
import numpy as np


class LinearModelTrainer:
    """
    Class untuk training model Linear Regression dengan Pipeline.
    Features: year, mileage, engineSize, model, transmission, fuelType.
    """
    
    def __init__(self, brand_name):
        self.brand_name = brand_name
        self.model = None
        self.metrics = {}
        self.log = []
    
    def load_and_preprocess_data(self, excel_file_path):
        """
        Load data dari Excel dan lakukan preprocessing.
        
        Args:
            excel_file_path: Path ke file Excel
            
        Returns:
            X: Features (DataFrame)
            y: Target (Series)
        """
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Membaca file: {os.path.basename(excel_file_path)}")
        
        # 1. Baca Excel dengan deteksi engine otomatis
        try:
            file_ext = os.path.splitext(excel_file_path)[1].lower()
            
            if file_ext == '.xlsx':
                df = pd.read_excel(excel_file_path, engine='openpyxl')
            elif file_ext == '.xls':
                df = pd.read_excel(excel_file_path, engine='xlrd')
            elif file_ext == '.csv':
                df = pd.read_csv(excel_file_path)
            else:
                # Default openpyxl untuk format modern
                df = pd.read_excel(excel_file_path, engine='openpyxl')
                
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Data berhasil dibaca: {len(df)} baris")
        except Exception as e:
            raise ValueError(f"Error membaca file Excel: {str(e)}")
        
        # 2. Support kolom Bahasa Inggris & Indonesia + mapping ke format standard
        column_mapping = {
            # Year variations
            'tahun': 'year',
            'thn': 'year',
            
            # Mileage variations
            'jarak_tempuh': 'mileage',
            'odometer': 'mileage',
            'km': 'mileage',
            'jarak': 'mileage',
            
            # Transmission variations
            'transmisi': 'transmission',
            'trans': 'transmission',
            'tranmission': 'transmission',  # common typo
            
            # FuelType variations
            'bahan_bakar': 'fuelType',
            'bahanbakar': 'fuelType',
            'bahan bakar': 'fuelType',
            'fuel': 'fuelType',
            'fueltype': 'fuelType',
            'fuel_type': 'fuelType',
            'jenis_bahan_bakar': 'fuelType',
            'type_fuel': 'fuelType',
            'bbm': 'fuelType',
            
            # Price variations
            'harga': 'price',
            'hrg': 'price',
            'harga_mobil': 'price',
            'harga mobil': 'price',
            'hargamobil': 'price',
            'nilai': 'price',
            'biaya': 'price',
            
            # EngineSize variations
            'cc': 'engineSize',
            'engine_size': 'engineSize',
            'enginesize': 'engineSize',
            'kapasitas_mesin': 'engineSize',
            'kapasitas': 'engineSize',
            'mesin': 'engineSize'
        }
        
        # Rename kolom ke format standard (lowercase dulu)
        df.columns = df.columns.str.lower().str.strip()
        
        # Debug: Log kolom asli sebelum mapping
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Kolom di Excel: {', '.join(df.columns.tolist())}")
        
        df = df.rename(columns=column_mapping)
        
        # Debug: Log kolom setelah mapping
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Kolom setelah mapping: {', '.join(df.columns.tolist())}")
        
        # 3. Validasi kolom yang diperlukan (format baru: English)
        required_columns = ['year', 'mileage', 'transmission', 'fuelType', 'price']
        
        # engineSize dan model opsional, tapi akan di-handle
        if 'engineSize' not in df.columns:
            df['engineSize'] = 1500  # Default CC
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Kolom engineSize tidak ada, menggunakan default: 1500")
        
        if 'model' not in df.columns:
            df['model'] = 'Unknown'  # Default model name
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Kolom model tidak ada, menggunakan default: Unknown")
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            available_cols = ', '.join(df.columns.tolist())
            raise ValueError(
                f"❌ Kolom tidak ditemukan: {', '.join(missing_columns)}.\n\n"
                f"📋 Kolom yang tersedia di Excel: {available_cols}\n\n"
                f"✅ Kolom yang diperlukan:\n"
                f"   • year / tahun / thn\n"
                f"   • mileage / jarak_tempuh / odometer / km\n"
                f"   • transmission / transmisi\n"
                f"   • fuelType / bahan_bakar / fuel / bbm\n"
                f"   • price / harga\n\n"
                f"💡 Tip: Pastikan nama kolom ditulis dengan benar (huruf besar/kecil tidak masalah)"
            )
        
        # 4. Bersihkan data numerik (convert format teks ke angka)
        def clean_numeric(value):
            """Convert berbagai format teks ke angka"""
            if pd.isna(value):
                return value
            if isinstance(value, (int, float)):
                return value
            
            # Convert ke string dan lowercase
            value = str(value).lower().strip()
            
            # Hapus prefix Rp, IDR, dll
            value = value.replace('rp', '').replace('idr', '').replace('rupiah', '')
            
            # Hapus unit km, ribu, rb, jt, juta, m, mil, dsb
            value = value.replace('km', '').replace('ribu', '000').replace('rb', '000')
            value = value.replace('jt', '000000').replace('juta', '000000')
            value = value.replace('m', '000000').replace('mil', '000000')
            value = value.replace('milyar', '000000000').replace('miliar', '000000000')
            
            # Hapus separator titik, koma, spasi
            value = value.replace('.', '').replace(',', '').replace(' ', '').replace('_', '')
            
            # Hapus karakter non-numeric lainnya kecuali minus
            value = ''.join(c for c in value if c.isdigit() or c == '-' or c == '.')
            
            if not value or value == '' or value == '-':
                return None
            
            try:
                return float(value)
            except:
                return None
        
        # Apply cleaning ke kolom numerik dengan detailed logging
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Cleaning numeric columns...")
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Data before numeric cleaning: {len(df)} rows")
        
        for col in ['year', 'mileage', 'price', 'engineSize']:
            if col in df.columns:
                # Log sample values SEBELUM cleaning
                sample_before = df[col].head(5).tolist()
                self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {col} - Sample BEFORE cleaning: {sample_before}")
                
                before_clean = df[col].notna().sum()
                df[col] = df[col].apply(clean_numeric)
                after_clean = df[col].notna().sum()
                
                # Log sample values SETELAH cleaning
                sample_after = df[col].head(5).tolist()
                self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {col} - Sample AFTER cleaning: {sample_after}")
                
                nan_created = before_clean - after_clean
                if nan_created > 0:
                    self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}]   ⚠️ {col}: {nan_created} values became NaN after cleaning ({nan_created/len(df)*100:.1f}%)")
                else:
                    self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}]   ✓ {col}: {after_clean} valid values")
        
        # Fill NaN di engineSize dengan default value (karena engineSize optional)
        if 'engineSize' in df.columns:
            nan_count = df['engineSize'].isna().sum()
            if nan_count > 0:
                df['engineSize'] = df['engineSize'].fillna(1500)
                self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Filled {nan_count} missing engineSize dengan default 1500cc")
        
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Data numerik dibersihkan - {len(df)} rows remaining")
        
        # 5. Standardize categorical values dengan handling unknown values
        # Transmission: Manual/Automatic
        if 'transmission' in df.columns:
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Standardizing transmission values...")
            
            # Convert to string, handle NaN
            df['transmission'] = df['transmission'].fillna('unknown')  # Fill NaN dulu
            df['transmission'] = df['transmission'].astype(str).str.lower().str.strip()
            
            # Log unique values sebelum mapping
            unique_trans = df['transmission'].unique()
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}]   Unique transmission values: {', '.join(map(str, unique_trans[:10]))}")
            
            # Mapping dengan lebih banyak variasi
            df['transmission'] = df['transmission'].replace({
                'mt': 'Manual',
                'manual': 'Manual',
                'm': 'Manual',
                'matic': 'Automatic',
                'at': 'Automatic',
                'automatic': 'Automatic',
                'otomatis': 'Automatic',
                'a': 'Automatic',
                'cvt': 'Automatic',
                'amt': 'Automatic',
                'nan': 'Manual',  # Handle 'nan' string
                'unknown': 'Manual',
                'none': 'Manual'
            })
            
            # Handle unknown values - set ke Manual sebagai default
            unknown_mask = ~df['transmission'].isin(['Manual', 'Automatic'])
            unknown_count = unknown_mask.sum()
            if unknown_count > 0:
                unknown_vals = df.loc[unknown_mask, 'transmission'].unique()[:5]
                self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}]   ⚠️ Found {unknown_count} unknown transmission values: {', '.join(map(str, unknown_vals))}")
                df.loc[unknown_mask, 'transmission'] = 'Manual'  # Default ke Manual
                self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}]   → Set to 'Manual' as default")
            
            # Final check - pastikan tidak ada NaN
            final_na = df['transmission'].isna().sum()
            if final_na > 0:
                self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}]   ⚠️ {final_na} NaN values in transmission, filling with 'Manual'")
                df['transmission'] = df['transmission'].fillna('Manual')
        
        # FuelType: Petrol/Diesel
        if 'fuelType' in df.columns:
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Standardizing fuelType values...")
            
            # Convert to string, handle NaN
            df['fuelType'] = df['fuelType'].fillna('unknown')  # Fill NaN dulu
            df['fuelType'] = df['fuelType'].astype(str).str.lower().str.strip()
            
            # Log unique values sebelum mapping
            unique_fuel = df['fuelType'].unique()
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}]   Unique fuelType values: {', '.join(map(str, unique_fuel[:10]))}")
            
            # Mapping dengan lebih banyak variasi
            df['fuelType'] = df['fuelType'].replace({
                'bensin': 'Petrol',
                'petrol': 'Petrol',
                'gasoline': 'Petrol',
                'premium': 'Petrol',
                'pertamax': 'Petrol',
                'gas': 'Petrol',
                'diesel': 'Diesel',
                'solar': 'Diesel',
                'diessel': 'Diesel',  # common typo
                'nan': 'Petrol',  # Handle 'nan' string
                'unknown': 'Petrol',
                'none': 'Petrol'
            })
            
            # Handle unknown values - set ke Petrol sebagai default
            unknown_mask = ~df['fuelType'].isin(['Petrol', 'Diesel'])
            unknown_count = unknown_mask.sum()
            if unknown_count > 0:
                unknown_vals = df.loc[unknown_mask, 'fuelType'].unique()[:5]
                self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}]   ⚠️ Found {unknown_count} unknown fuelType values: {', '.join(map(str, unknown_vals))}")
                df.loc[unknown_mask, 'fuelType'] = 'Petrol'  # Default ke Petrol
                self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}]   → Set to 'Petrol' as default")
            
            # Final check - pastikan tidak ada NaN
            final_na = df['fuelType'].isna().sum()
            if final_na > 0:
                self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}]   ⚠️ {final_na} NaN values in fuelType, filling with 'Petrol'")
                df['fuelType'] = df['fuelType'].fillna('Petrol')
        
        # 6. Diagnostic: Check NaN count per column sebelum dropna
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] === Checking Missing Values Before Dropna ===")
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Total rows: {len(df)}")
        
        missing_info = {}
        for col in ['year', 'mileage', 'engineSize', 'transmission', 'fuelType', 'price']:
            if col in df.columns:
                na_count = df[col].isna().sum()
                missing_info[col] = na_count
                if na_count > 0:
                    self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}]   ❌ {col}: {na_count} missing values ({na_count/len(df)*100:.1f}%)")
                else:
                    self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}]   ✓ {col}: 0 missing values")
        
        # 7. Data Cleaning - Drop missing values dan duplicates
        # engineSize sudah di-handle dengan fillna, jadi tidak perlu di-check di sini
        initial_rows = len(df)
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Dropping rows with missing values in required columns...")
        df = df.dropna(subset=['year', 'mileage', 'transmission', 'fuelType', 'price'])
        dropped_na = initial_rows - len(df)
        
        if len(df) == 0:
            # Buat error message yang informatif
            error_msg = f"❌ Semua {initial_rows} baris data terhapus saat membersihkan missing values!\n\n"
            error_msg += "📋 Kolom yang memiliki missing values:\n"
            for col, count in missing_info.items():
                if col != 'engineSize' and count > 0:  # engineSize optional
                    error_msg += f"   • {col}: {count} missing ({count/initial_rows*100:.1f}%)\n"
            error_msg += "\n💡 Kemungkinan penyebab:\n"
            error_msg += "   1. Kolom di Excel tidak ter-mapping dengan benar\n"
            error_msg += "   2. Format data tidak sesuai (contoh: text di kolom numeric)\n"
            error_msg += "   3. Kolom transmission/fuelType berisi nilai yang tidak valid\n"
            error_msg += "\n✅ Solusi:\n"
            error_msg += "   - Periksa kembali nama kolom di Excel\n"
            error_msg += "   - Pastikan format data sudah benar (year=angka, price=angka, dll)\n"
            error_msg += "   - Lihat log di atas untuk detail kolom yang ter-mapping\n"
            raise ValueError(error_msg)
        
        if dropped_na > 0:
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Dihapus {dropped_na} baris dengan data kosong ({len(df)} rows remaining)")
        
        # Drop duplicates
        before_dup = len(df)
        df = df.drop_duplicates()
        dropped_dup = before_dup - len(df)
        if dropped_dup > 0:
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Dihapus {dropped_dup} baris duplikat ({len(df)} rows remaining)")
        
        # 8. Range Filtering - dengan check data actual terlebih dahulu
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] === Checking Data Ranges ===")
        try:
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Year: {int(df['year'].min())} - {int(df['year'].max())}")
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Price: Rp {df['price'].min():,.0f} - Rp {df['price'].max():,.0f}")
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Mileage: {df['mileage'].min():,.0f} - {df['mileage'].max():,.0f} km")
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] EngineSize: {df['engineSize'].min():,.0f} - {df['engineSize'].max():,.0f} cc")
        except Exception as e:
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Warning: Tidak bisa menampilkan data ranges - {str(e)}")
        
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Menerapkan range filtering...")
        
        # Year: 2010-2025 (lebih flexible)
        before = len(df)
        df = df[(df['year'] >= 2010) & (df['year'] <= 2025)]
        dropped = before - len(df)
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}]   → Year filter (2010-2025): {before} → {len(df)} baris ({dropped} dihapus)")
        
        if len(df) == 0:
            raise ValueError(f"❌ Semua data dihapus di Year filter. Data year harus antara 2010-2025.")
        
        # Price: 50 juta - 1 miliar (lebih flexible)
        before = len(df)
        df = df[(df['price'] >= 50_000_000) & (df['price'] <= 1_000_000_000)]
        dropped = before - len(df)
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}]   → Price filter (50M-1B): {before} → {len(df)} baris ({dropped} dihapus)")
        
        if len(df) == 0:
            raise ValueError(f"❌ Semua data dihapus di Price filter. Data price harus antara Rp 50 juta - Rp 1 miliar.")
        
        # Mileage: 0 - 300k km (lebih flexible)
        before = len(df)
        df = df[(df['mileage'] >= 0) & (df['mileage'] <= 300_000)]
        dropped = before - len(df)
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}]   → Mileage filter (0-300k km): {before} → {len(df)} baris ({dropped} dihapus)")
        
        if len(df) == 0:
            raise ValueError(f"❌ Semua data dihapus di Mileage filter. Data mileage harus antara 0 - 300,000 km.")
        
        # EngineSize: 800-5000 cc (lebih flexible)
        before = len(df)
        df = df[(df['engineSize'] >= 800) & (df['engineSize'] <= 5000)]
        dropped = before - len(df)
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}]   → EngineSize filter (800-5000cc): {before} → {len(df)} baris ({dropped} dihapus)")
        
        if len(df) == 0:
            raise ValueError(f"❌ Semua data dihapus di EngineSize filter. Data engineSize harus antara 800 - 5000 cc.")
        
        # 9. IQR Outlier Removal untuk price (hanya jika data cukup banyak)
        if len(df) >= 30:  # Minimal 30 data untuk IQR removal
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Menghapus outliers dengan IQR method...")
            Q1 = df['price'].quantile(0.25)
            Q3 = df['price'].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            before = len(df)
            df = df[(df['price'] >= lower_bound) & (df['price'] <= upper_bound)]
            removed_outliers = before - len(df)
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}]   → Removed {removed_outliers} outliers: {before} → {len(df)} baris")
        else:
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Skip IQR outlier removal (data < 30 baris)")
        
        if len(df) < 10:
            raise ValueError(f"Data terlalu sedikit setelah preprocessing: {len(df)} baris. Minimal 10 baris diperlukan.")
        
        # Summary
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] === Data Cleaning Summary ===")
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Final shape: {len(df)} baris")
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Year range: {int(df['year'].min())}-{int(df['year'].max())}")
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Price range: Rp {df['price'].min():,.0f} - Rp {df['price'].max():,.0f}")
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Price mean: Rp {df['price'].mean():,.0f}")
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Unique models: {df['model'].nunique()}")
        
        # 10. Pisahkan Features dan Target
        # Features: year, mileage, engineSize (numeric) + model, transmission, fuelType (categorical)
        feature_columns = ['year', 'mileage', 'engineSize', 'model', 'transmission', 'fuelType']
        X = df[feature_columns]
        y = df['price']
        
        return X, y
    
    def train_model(self, X, y):
        """
        Latih model Linear Regression dengan Pipeline.
        Pipeline: ColumnTransformer (passthrough numeric, OneHotEncode categorical) + LinearRegression
        
        Args:
            X: Features DataFrame dengan kolom: year, mileage, engineSize, model, transmission, fuelType
            y: Target pandas Series (price)
        """
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Memulai training Linear Regression dengan Pipeline...")
        
        # 1. Split data 80% train, 20% test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=10
        )
        
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Split data: {len(X_train)} train, {len(X_test)} test")
        
        # 2. Setup Pipeline yang sama dengan model lama
        # Numeric features: passthrough (no scaling)
        # Categorical features: OneHotEncoder
        numeric_features = ['year', 'mileage', 'engineSize']
        categorical_features = ['model', 'transmission', 'fuelType']
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', 'passthrough', numeric_features),
                ('cat', OneHotEncoder(drop='first', handle_unknown='ignore', sparse_output=False), categorical_features)
            ]
        )
        
        # Pipeline: preprocessor + regressor
        self.model = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', LinearRegression())
        ])
        
        # 3. Training
        self.model.fit(X_train, y_train)
        
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Training selesai!")
        
        # 4. Prediksi dan Evaluasi
        y_pred = self.model.predict(X_test)
        
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        mape = mean_absolute_percentage_error(y_test, y_pred) * 100
        
        # Hitung RMSE percentage (relatif terhadap rata-rata harga)
        mean_price = np.mean(y_test)
        rmse_percentage = (rmse / mean_price) * 100
        
        self.metrics = {
            'rmse': float(rmse),
            'mae': float(mae),
            'r2_score': float(r2),
            'accuracy_percentage': float(r2 * 100),
            'rmse_percentage': float(rmse_percentage),
            'mape': float(mape)
        }
        
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] === Hasil Evaluasi ===")
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] R² Score: {r2:.4f} ({r2*100:.2f}%)")
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] RMSE: Rp {rmse:,.0f} ({rmse_percentage:.2f}%)")
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] MAE: Rp {mae:,.0f}")
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] MAPE: {mape:.2f}%")
        
        # Performance assessment
        if r2 >= 0.80 and rmse_percentage <= 20:
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ MODEL PERFORMANCE: EXCELLENT")
        elif r2 >= 0.70:
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ MODEL PERFORMANCE: GOOD")
        else:
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ MODEL NEEDS IMPROVEMENT")
        
        return self.metrics
    
    def save_model(self, model_dir='ml_models'):
        """
        Simpan model ke file .pkl dengan format <Brand>_Model.pkl
        (Brand dengan huruf pertama kapital untuk konsistensi)
        
        Args:
            model_dir: Direktori untuk menyimpan model
        """
        if self.model is None:
            raise ValueError("Model belum dilatih. Panggil train_model() terlebih dahulu.")
        
        # Pastikan direktori ada
        model_path = os.path.join(settings.BASE_DIR, model_dir)
        os.makedirs(model_path, exist_ok=True)
        
        # Format nama file: <Brand>_Model.pkl (capitalize untuk konsistensi)
        model_filename = f"{self.brand_name.capitalize()}_Model.pkl"
        full_path = os.path.join(model_path, model_filename)
        
        # Simpan model menggunakan joblib (overwrite jika sudah ada)
        joblib.dump(self.model, full_path)
        
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Model disimpan: {model_filename}")
        
        return full_path


def train_from_file(file_dataset_id):
    """
    Fungsi utama untuk training dari FileDataset.
    
    Args:
        file_dataset_id: ID dari FileDataset yang akan ditraining
        
    Returns:
        dict: Hasil training dengan keys: success, message, metrics, log
    """
    from .models import FileDataset
    
    try:
        # 1. Ambil FileDataset
        file_dataset = FileDataset.objects.get(id=file_dataset_id)
        brand_name = file_dataset.brand.name
        excel_path = file_dataset.file_excel.path
        
        start_time = datetime.now()
        
        # 2. Inisialisasi trainer
        trainer = LinearModelTrainer(brand_name)
        
        # 3. Load dan preprocess data
        X, y = trainer.load_and_preprocess_data(excel_path)
        
        # 4. Training
        metrics = trainer.train_model(X, y)
        
        # 5. Simpan model
        model_path = trainer.save_model()
        
        # 6. Hitung waktu training
        end_time = datetime.now()
        training_time = (end_time - start_time).total_seconds()
        
        trainer.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Training selesai dalam {training_time:.2f} detik")
        
        # 7. Clear cache model (jika ada)
        from .logika_ml import _ml_models_cache
        brand_key = brand_name.lower()
        if brand_key in _ml_models_cache:
            del _ml_models_cache[brand_key]
            trainer.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Cache model cleared")
        
        return {
            'success': True,
            'message': f"Training berhasil! Model {brand_name} telah diupdate.",
            'metrics': metrics,
            'log': trainer.log,
            'training_time': training_time
        }
            
    except Exception as e:
        return {
            'success': False,
            'message': f"Error: {str(e)}",
            'metrics': {},
            'log': []
        }
