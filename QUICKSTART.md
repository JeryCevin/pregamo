# 🚀 Quick Start - Autonomous Training

Panduan cepat untuk menjalankan sistem autonomous training.

## ⚡ Quick Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run migrations
python manage.py migrate

# 3. Install Redis (Windows)
# Download dari: https://github.com/microsoftarchive/redis/releases
# Atau: choco install redis-64
```

## 🏃 Running (3 Terminals)

### Terminal 1: Django
```bash
python manage.py runserver
```

### Terminal 2: Celery Worker
```bash
celery -A config worker --loglevel=info --pool=solo
```

### Terminal 3: Celery Beat (Scheduler)
```bash
celery -A config beat --loglevel=info
```

## 🎯 Usage

### 1. Auto-Train (Upload Dataset)
```
Admin → Manage Datasets → Add Dataset → Upload Excel
→ Training otomatis dimulai! 🤖
→ Check: Training History
```

### 2. Manual Train
```
Admin → Train Models → Pilih Brand → Train
→ Background task started! 🚀
→ Check: Training History
```

### 3. Monitor
```
Admin → Training History
→ Lihat status: Pending/Processing/Completed/Failed
→ Lihat metrics: RMSE, MAE, R² Score
```

## 🔧 Management Commands

```bash
# Train semua models (async)
python manage.py train_all_models --async

# Train brand tertentu
python manage.py train_all_models --brand Toyota

# Check Celery status
python manage.py check_celery
```

## 📊 Monitoring

```bash
# Check active tasks
celery -A config inspect active

# Check workers
celery -A config inspect stats

# Check scheduled tasks
celery -A config inspect scheduled
```

## ⚠️ Troubleshooting

### Celery tidak connect
```bash
# Pastikan Redis running
redis-server

# Atau gunakan memory broker (development)
# Edit config/settings.py:
CELERY_BROKER_URL = 'memory://'
```

### Worker tidak start
```bash
# Windows: gunakan --pool=solo
celery -A config worker --loglevel=info --pool=solo
```

### Training tidak auto-trigger
```bash
# Check signals loaded
python manage.py shell
>>> import prediction.signals
>>> # No error = OK

# Check worker running
python manage.py check_celery
```

## 📖 Full Documentation
Lihat: [AUTONOMOUS_TRAINING_SETUP.md](AUTONOMOUS_TRAINING_SETUP.md)

---

## ✅ Features Checklist

- ✅ Auto-train saat upload dataset
- ✅ Background training (non-blocking)
- ✅ Scheduled retraining (daily + health check)
- ✅ Training history monitoring
- ✅ Management commands
- ✅ Celery status checker
- ✅ Fallback ke synchronous jika Celery off

**System ready! 🎉**
