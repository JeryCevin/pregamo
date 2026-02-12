# prediction/training_linear.py
"""
Modul untuk training model Linear Regression sederhana.
Fokus pada workflow: Upload Excel → Preprocess → Train → Save Model.
"""

import os
import pandas as pd
import joblib
from datetime import datetime
from django.conf import settings
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import numpy as np


class LinearModelTrainer:
    """
    Class untuk training model Linear Regression.
    Menggunakan 4 fitur sederhana: tahun, jarak_tempuh, transmisi, bahan_bakar.
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
        
        # 2. Validasi kolom yang diperlukan
        required_columns = ['tahun', 'jarak_tempuh', 'transmisi', 'bahan_bakar', 'harga']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Kolom tidak ditemukan: {', '.join(missing_columns)}. Pastikan Excel memiliki kolom: {', '.join(required_columns)}")
        
        # 3. Drop baris kosong
        initial_rows = len(df)
        df = df.dropna(subset=required_columns)
        dropped_rows = initial_rows - len(df)
        if dropped_rows > 0:
            self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Dihapus {dropped_rows} baris dengan data kosong")
        
        # 4. Preprocessing: Mapping Transmisi
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Melakukan preprocessing...")
        
        transmisi_mapping = {
            'Manual': 0,
            'manual': 0,
            'MT': 0,
            'Matic': 1,
            'matic': 1,
            'Automatic': 1,
            'automatic': 1,
            'AT': 1
        }
        df['transmisi'] = df['transmisi'].map(transmisi_mapping)
        
        # 5. Preprocessing: Mapping Bahan Bakar
        fuel_mapping = {
            'Bensin': 1,
            'bensin': 1,
            'Petrol': 1,
            'petrol': 1,
            'Gasoline': 1,
            'gasoline': 1,
            'Diesel': 0,
            'diesel': 0,
            'Solar': 0,
            'solar': 0
        }
        df['bahan_bakar'] = df['bahan_bakar'].map(fuel_mapping)
        
        # 6. Drop baris yang gagal di-mapping
        df = df.dropna(subset=['transmisi', 'bahan_bakar'])
        
        if len(df) < 10:
            raise ValueError(f"Data terlalu sedikit setelah preprocessing: {len(df)} baris. Minimal 10 baris diperlukan.")
        
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Data setelah preprocessing: {len(df)} baris")
        
        # 7. Pisahkan Features dan Target
        X = df[['tahun', 'jarak_tempuh', 'transmisi', 'bahan_bakar']]
        y = df['harga']
        
        return X, y
    
    def train_model(self, X, y):
        """
        Latih model Linear Regression.
        
        Args:
            X: Features
            y: Target
        """
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Memulai training Linear Regression...")
        
        # 1. Split data 80% train, 20% test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Split data: {len(X_train)} train, {len(X_test)} test")
        
        # 2. Training
        self.model = LinearRegression()
        self.model.fit(X_train, y_train)
        
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Training selesai!")
        
        # 3. Prediksi dan Evaluasi
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
        Simpan model ke file .pkl dengan format <brand>_Model.pkl
        
        Args:
            model_dir: Direktori untuk menyimpan model
        """
        if self.model is None:
            raise ValueError("Model belum dilatih. Panggil train_model() terlebih dahulu.")
        
        # Pastikan direktori ada
        model_path = os.path.join(settings.BASE_DIR, model_dir)
        os.makedirs(model_path, exist_ok=True)
        
        # Format nama file: <Brand>_Model.pkl
        model_filename = f"{self.brand_name}_Model.pkl"
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
