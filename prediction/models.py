# prediction/models.py

from django.db import models
from django.contrib.auth.models import User

class Brand(models.Model):
    name = models.CharField(max_length=50, unique=True)
    # TAMBAHKAN BARIS INI
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    def __str__(self):
        return self.name

class CarModel(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.brand.name} {self.name}"
    
class PredictionHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Terhubung ke user (Jery Cevin)
    brand = models.CharField(max_length=50)
    model_name = models.CharField(max_length=100)
    year = models.IntegerField()
    mileage = models.IntegerField()
    transmission = models.CharField(max_length=20)
    fuel = models.CharField(max_length=20)
    engine_cc = models.IntegerField()
    predicted_price = models.BigIntegerField() # Harga hasil prediksi
    created_at = models.DateTimeField(auto_now_add=True) # Waktu otomatis saat tombol diklik

    def __str__(self):
        return f"{self.user.username} - {self.brand} {self.model_name}"


class CarDataset(models.Model):
    """
    Model untuk menyimpan dataset mobil bekas yang akan digunakan 
    untuk melatih model Machine Learning prediksi harga.
    [DEPRECATED] - Gunakan FileDataset untuk workflow baru
    """
    brand = models.CharField(max_length=50, verbose_name="Brand Mobil")
    model = models.CharField(max_length=50, verbose_name="Model Mobil")
    tahun = models.IntegerField(verbose_name="Tahun Produksi")
    jarak_tempuh = models.IntegerField(verbose_name="Jarak Tempuh (km)")
    transmisi = models.CharField(max_length=20, verbose_name="Transmisi")
    bahan_bakar = models.CharField(max_length=20, verbose_name="Bahan Bakar")
    cc = models.IntegerField(verbose_name="CC Mesin")
    harga = models.BigIntegerField(verbose_name="Harga (Rupiah)")
    
    # Field tambahan untuk tracking
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Tanggal Ditambahkan")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Tanggal Diupdate")
    
    class Meta:
        verbose_name = "Data Mobil Bekas (Legacy)"
        verbose_name_plural = "Manage Datasets (Legacy)"
        ordering = ['-created_at']  # Urutkan dari yang terbaru
        indexes = [
            models.Index(fields=['brand', 'model']),  # Index untuk pencarian cepat
            models.Index(fields=['tahun']),
        ]
    
    def __str__(self):
        return f"{self.brand} {self.model} - {self.tahun}"


class FileDataset(models.Model):
    """
    Model untuk upload file Excel dataset per brand.
    Workflow baru: Upload file → Train model langsung dari file.
    """
    brand = models.ForeignKey(
        Brand, 
        on_delete=models.CASCADE, 
        related_name='file_datasets',
        verbose_name="Brand Mobil"
    )
    file_excel = models.FileField(
        upload_to='datasets/',
        verbose_name="File Excel Dataset",
        help_text="Upload file Excel (.xlsx/.csv) dengan kolom: year/tahun, mileage/jarak_tempuh, transmission/transmisi, fuelType/bahan_bakar, price/harga. Opsional: model, engineSize/cc"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Tanggal Upload")
    file_size = models.IntegerField(default=0, verbose_name="Ukuran File (bytes)", blank=True)
    row_count = models.IntegerField(default=0, verbose_name="Jumlah Baris Data", blank=True)
    description = models.TextField(blank=True, verbose_name="Deskripsi/Catatan")
    
    class Meta:
        verbose_name = "Dataset File"
        verbose_name_plural = "Manage Datasets"
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['brand', '-uploaded_at']),
        ]
    
    def __str__(self):
        return f"{self.brand.name} - {self.file_excel.name} ({self.uploaded_at.strftime('%Y-%m-%d')})"
    
    def get_file_size_display(self):
        """Format ukuran file dalam KB/MB"""
        if self.file_size < 1024:
            return f"{self.file_size} bytes"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.2f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.2f} MB"
    
    def save(self, *args, **kwargs):
        """Override save untuk hitung ukuran file otomatis"""
        if self.file_excel:
            self.file_size = self.file_excel.size
        super().save(*args, **kwargs)


class TrainingHistory(models.Model):
    """
    Model untuk menyimpan riwayat training model ML.
    Berguna untuk tracking performa model setiap kali dilatih ulang.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    brand = models.CharField(max_length=50, verbose_name="Brand Mobil")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    
    # Data metrics
    total_data = models.IntegerField(default=0, verbose_name="Total Data")
    data_cleaned = models.IntegerField(default=0, verbose_name="Data Setelah Cleaning")
    data_removed = models.IntegerField(default=0, verbose_name="Data Dihapus")
    
    # Model performance
    rmse = models.FloatField(null=True, blank=True, verbose_name="RMSE")
    mae = models.FloatField(null=True, blank=True, verbose_name="MAE")
    r2_score = models.FloatField(null=True, blank=True, verbose_name="R² Score")
    
    # Training details
    model_path = models.CharField(max_length=255, blank=True, verbose_name="Path Model")
    training_time = models.FloatField(null=True, blank=True, verbose_name="Waktu Training (detik)")
    
    # Log & errors
    log_message = models.TextField(blank=True, verbose_name="Log Pesan")
    error_message = models.TextField(blank=True, verbose_name="Error Message")
    
    # Tracking
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Mulai Training")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Selesai Training")
    trained_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Dilatih Oleh")
    
    class Meta:
        verbose_name = "Training Model"
        verbose_name_plural = "Train Models"
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['brand', 'status']),
            models.Index(fields=['-started_at']),
        ]
    
    def __str__(self):
        return f"{self.brand} - {self.status} ({self.started_at.strftime('%Y-%m-%d %H:%M')})"
    
    def get_accuracy_percentage(self):
        """Konversi R² score ke persentase akurasi"""
        if self.r2_score is not None:
            return round(self.r2_score * 100, 2)
        return None
