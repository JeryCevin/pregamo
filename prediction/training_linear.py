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
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
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
            'tahun': 'year',
            'jarak_tempuh': 'mileage',
            'odometer': 'mileage',
            'transmisi': 'transmission',
            'bahan_bakar': 'fuelType',
            'fuel': 'fuelType',
            'fuel_type': 'fuelType',
            'harga': 'price',
            'cc': 'engineSize',
            'engine_size': 'engineSize',
            'kapasitas_mesin': 'engineSize'
        }
        
        # Rename kolom ke format standard (lowercase dulu)
        df.columns = df.columns.str.lower()
        df = df.rename(columns=column_mapping)
        
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
            raise ValueError(
                f"Kolom tidak ditemukan: {', '.join(missing_columns)}. "
                f"Pastikan Excel memiliki kolom: year/tahun, mileage/jarak_tempuh, "
                f"transmission/transmisi, fuelType/bahan_bakar, price/harga"
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
            
            # Hapus unit km, ribu, rb, jt, juta, m, mil, dsb
            value = value.replace('km', '').replace('ribu', '000').replace('rb', '000')
            value = value.replace('jt', '000000').replace('juta', '000000')
            value = value.replace('m', '000000').replace('mil', '000000')
            value = value.replace('milyar', '000000000').replace('miliar', '000000000')
            
            # Hapus separator titik, koma, spasi
            value = value.replace('.', '').replace(',', '').replace(' ', '')
            
            try:
                return float(value)
            except:
                return None
        
        # Apply cleaning ke kolom numerik
        for col in ['year', 'mileage', 'price', 'engineSize']:
            if col in df.columns:
                df[col] = df[col].apply(clean_numeric)
        
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Data numerik dibersihkan")
        
        # 5. Standardize categorical values
        # Transmission: Manual/Automatic
        if 'transmission' in df.columns:
            df['transmission'] = df['transmission'].astype(str).str.lower()
            df['transmission'] = df['transmission'].replace({
                'mt': 'Manual',
                'manual': 'Manual',
                'matic': 'Automatic',
                'at': 'Automatic',
                'automatic': 'Automatic'
            })
        
        # FuelType: Petrol/Diesel
        if 'fuelType' in df.columns:
            df['fuelType'] = df['fuelType'].astype(str).str.lower()
            df['fuelType'] = df['fuelType'].replace({
                'bensin': 'Petrol',
                'petrol': 'Petrol',
                'gasoline': 'Petrol',
                'diesel': 'Diesel',
                'solar': 'Diesel'
            })
        
        # 6. Drop baris kosong
        initial_rows = len(df)
        df = df.dropna(subset=['year', 'mileage', 'transmission', 'fuelType', 'price'])
        dropped_rows = initial_rows - len(df)
        if dropped_rows > 0:
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Dihapus {dropped_rows} baris dengan data kosong")
        
        if len(df) < 10:
            raise ValueError(f"Data terlalu sedikit setelah preprocessing: {len(df)} baris. Minimal 10 baris diperlukan.")
        
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Data setelah preprocessing: {len(df)} baris")
        
        # 7. Pisahkan Features dan Target
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
            X, y, test_size=0.2, random_state=42
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
        
        self.metrics = {
            'rmse': float(rmse),
            'mae': float(mae),
            'r2_score': float(r2),
            'accuracy_percentage': float(r2 * 100)
        }
        
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] === Hasil Evaluasi ===")
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] RMSE: Rp {rmse:,.0f}")
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] MAE: Rp {mae:,.0f}")
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] R² Score: {r2:.4f} ({r2*100:.2f}%)")
        
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
