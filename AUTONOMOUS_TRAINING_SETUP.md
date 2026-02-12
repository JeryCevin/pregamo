# 🤖 Autonomous Training Setup Guide

Sistem training model kini **fully autonomous** dan berjalan di background tanpa blocking.

## 🎯 Fitur Autonomous Training

### 1. **Auto-Train saat Upload Dataset** ✨
- Training otomatis ter-trigger saat upload dataset baru
- Tidak perlu manual train lagi setelah upload
- Berjalan di background via Celery

### 2. **Scheduled Retraining** ⏰
- **Daily Retrain**: Semua model di-retrain otomatis setiap hari jam 02:00
- **Health Check**: Check performa model setiap 6 jam
- **Auto-Retrain**: Retrain otomatis jika:
  - Model belum pernah dilatih
  - Training terakhir > 7 hari
  - Ada dataset baru setelah training terakhir

### 3. **Background Processing** 🚀
- Training tidak blocking request
- Admin bisa langsung lanjut kerja
- Monitor progress via Training History

---

## 📦 Installation & Setup

### Step 1: Install Dependencies

```bash
# Install packages baru
pip install celery redis django-celery-beat django-celery-results

# Atau install semua dari requirements.txt
pip install -r requirements.txt
```

### Step 2: Install & Run Redis (Message Broker)

**Windows:**
```bash
# Download Redis for Windows dari:
# https://github.com/microsoftarchive/redis/releases

# Atau install via Chocolatey:
choco install redis-64

# Run Redis server:
redis-server
```

**Alternative - Menggunakan Memory Broker (Development)**
Edit `config/settings.py`:
```python
# Ganti ini:
CELERY_BROKER_URL = 'redis://localhost:6379/0'

# Dengan ini (untuk dev tanpa Redis):
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'django-db'
```

### Step 3: Run Migrations

```bash
# Migrate django-celery-beat dan django-celery-results
python manage.py migrate
```

### Step 4: Create Logs Directory

```bash
# Windows PowerShell
mkdir logs

# Atau manual create folder 'logs' di root project
```

---

## 🚀 Running the System

Untuk sistem autonomous bekerja, jalankan **3 process** ini:

### Terminal 1: Django Development Server
```bash
python manage.py runserver
```

### Terminal 2: Celery Worker (Background Tasks)
```bash
# Windows
celery -A config worker --loglevel=info --pool=solo

# Linux/Mac
celery -A config worker --loglevel=info
```

### Terminal 3: Celery Beat (Scheduler untuk Periodic Tasks)
```bash
celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

---

## 📊 Monitoring & Usage

### 1. **Upload Dataset** (Auto-Train Triggered)
1. Admin → `Manage Datasets`
2. Upload file Excel
3. **Training otomatis dimulai di background** ✅
4. Check progress di `Training History`

### 2. **Manual Train via Admin**
1. Admin → `Train Models`
2. Pilih Brand → klik Train
3. Task ter-queue di background
4. Lihat Task ID dan monitor di Training History

### 3. **Monitor Training History**
Admin → `Training History` untuk melihat:
- Status: Pending / Processing / Completed / Failed
- Metrics: RMSE, MAE, R² Score
- Training Time
- Logs lengkap

### 4. **Monitor Celery Tasks**
```bash
# Lihat task yang sedang berjalan
celery -A config inspect active

# Lihat registered tasks
celery -A config inspect registered

# Lihat scheduled tasks (Beat)
celery -A config inspect scheduled
```

---

## 🔧 Configuration

### Scheduled Tasks Settings
Edit `config/celery.py`:

```python
app.conf.beat_schedule = {
    # Retrain semua models setiap hari jam 2 pagi
    'retrain-all-models-daily': {
        'task': 'prediction.tasks.retrain_all_models',
        'schedule': crontab(hour=2, minute=0),  # Customize ini
    },
    
    # Check health setiap 6 jam
    'check-model-performance': {
        'task': 'prediction.tasks.check_and_retrain_if_needed',
        'schedule': crontab(hour='*/6', minute=0),  # Customize ini
    },
}
```

### Auto-Train on Upload
Enable/Disable di `prediction/signals.py`:

```python
# Untuk disable auto-train saat upload, comment signal ini:
@receiver(post_save, sender=FileDataset)
def auto_train_on_upload(sender, instance, created, **kwargs):
    # ...
```

---

## 🧪 Testing

### Test Manual Task
```python
# Django shell
python manage.py shell

# Test async training
from prediction.tasks import train_model_async
task = train_model_async.delay(file_dataset_id=1, user_id=1)
print(f"Task ID: {task.id}")

# Check task status
from celery.result import AsyncResult
result = AsyncResult(task.id)
print(f"Status: {result.status}")
print(f"Result: {result.result}")
```

### Test Scheduled Tasks
```python
# Test retrain all
from prediction.tasks import retrain_all_models
result = retrain_all_models()
print(result)

# Test health check
from prediction.tasks import check_and_retrain_if_needed
result = check_and_retrain_if_needed()
print(result)
```

---

## 🎛️ Celery Web Monitor (Optional)

Install Flower untuk monitoring GUI:

```bash
pip install flower

# Run Flower
celery -A config flower

# Access: http://localhost:5555
```

---

## 📋 Troubleshooting

### Problem: "No module named celery"
```bash
pip install celery redis django-celery-beat django-celery-results
```

### Problem: "Error connecting to Redis"
- Pastikan Redis server running: `redis-server`
- Atau gunakan memory broker (development only)

### Problem: "Task tidak jalan"
- Check Celery worker running di Terminal 2
- Check logs: `logs/celery.log`
- Check registered tasks: `celery -A config inspect registered`

### Problem: "Scheduled task tidak jalan"
- Pastikan Celery Beat running di Terminal 3
- Check beat schedule: `celery -A config inspect scheduled`
- Check django_celery_beat tables di database

### Problem: "Auto-train tidak trigger saat upload"
- Check signals loaded: ada `def ready()` di `prediction/apps.py`
- Check logs untuk error messages
- Pastikan Celery worker running

---

## 🌟 Production Deployment

### Using Supervisor (Linux)

Create supervisor config:

```ini
# /etc/supervisor/conf.d/celery.conf

[program:celery_worker]
command=/path/to/venv/bin/celery -A config worker --loglevel=info
directory=/path/to/project
user=www-data
autostart=true
autorestart=true

[program:celery_beat]
command=/path/to/venv/bin/celery -A config beat --loglevel=info
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
```

### Using systemd (Linux)

```ini
# /etc/systemd/system/celery.service

[Unit]
Description=Celery Worker
After=network.target

[Service]
Type=forking
User=www-data
WorkingDirectory=/path/to/project
ExecStart=/path/to/venv/bin/celery -A config worker --loglevel=info

[Install]
WantedBy=multi-user.target
```

---

## 📚 Available Tasks

### Background Tasks
- `prediction.tasks.train_model_async` - Async training untuk satu brand
- `prediction.tasks.retrain_all_models` - Retrain semua brand
- `prediction.tasks.check_and_retrain_if_needed` - Health check & auto-retrain
- `prediction.tasks.cleanup_old_training_logs` - Cleanup old logs

### Signals (Auto)
- `auto_train_on_upload` - Auto training saat upload dataset
- `update_row_count_on_upload` - Auto calculate row count

---

## 🎓 Summary

✅ **Auto-train saat upload** - Fully autonomous  
✅ **Scheduled retraining** - Daily & health check  
✅ **Background processing** - Non-blocking  
✅ **Monitoring** - Training History + Celery logs  
✅ **Scalable** - Ready untuk production  

**System kini fully autonomous!** 🎉
