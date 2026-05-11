# Project Skripsi

## Kesimpulan Analisis OOP

Berdasarkan struktur kode pada project ini, dua pilar OOP yang paling dominan adalah **inheritance** dan **encapsulation**.

### 1. Inheritance
Inheritance paling jelas terlihat pada beberapa class yang mewarisi class bawaan Django, seperti:
- `Brand`, `CarModel`, `CarDataset`, `FileDataset`, dan `TrainingHistory` yang mewarisi `models.Model`
- `DashboardConfig`, `PredictionConfig`, dan `AuthApiConfig` yang mewarisi `AppConfig`
- `CarDatasetAdmin`, `BrandAdmin`, `FileDatasetAdmin`, dan `TrainModelsAdmin` yang mewarisi class admin Django
- `TrainModelDataset` yang mewarisi `FileDataset`
- `TrainModelForm` yang mewarisi `forms.Form`

Pewarisan ini menunjukkan bahwa project memanfaatkan struktur class dari Django sebagai dasar pengembangan fitur.

### 2. Encapsulation
Encapsulation terlihat dari penggunaan class untuk membungkus data dan perilaku menjadi satu kesatuan. Contohnya:
- Model di `prediction/models.py` menyimpan atribut data sekaligus method seperti `__str__`, `save`, `get_file_size_display`, dan `get_accuracy_percentage`
- `LinearModelTrainer` di `prediction/training_linear.py` menyimpan state internal seperti `brand_name`, `model`, `metrics`, dan `log`
- Class admin di `prediction/admin.py` membungkus logika tampilan, validasi, dan aksi admin dalam satu class

Dengan cara ini, data dan proses yang berkaitan disatukan di dalam class masing-masing.

### 3. Polymorphism
Polymorphism juga digunakan, terutama melalui method overriding. Contohnya:
- Override `save()` pada `FileDataset`
- Override `get_urls()` pada beberapa class admin
- Override `save_model()` pada `FileDatasetAdmin`
- Override permission methods seperti `has_add_permission()`, `has_change_permission()`, dan `has_delete_permission()`

Polymorphism ini membuat perilaku class turunan bisa menyesuaikan kebutuhan tanpa mengubah struktur class induk.

### 4. Abstraction
Abstraction muncul dalam bentuk penyederhanaan proses yang kompleks menjadi interface yang lebih mudah dipakai. Contohnya:
- `LinearModelTrainer` menyembunyikan detail preprocessing dan training di balik method tertentu
- Fungsi `train_from_file()` menyederhanakan proses training menjadi satu pemanggilan saja
- Halaman admin menyembunyikan detail implementasi operasional di balik interface Django admin

Namun, abstraction formal dalam bentuk abstract class atau interface khusus belum banyak digunakan.

### Ringkasan
Secara umum, project ini paling dominan menggunakan **inheritance** dan **encapsulation**. Kedua pilar tersebut paling kuat terlihat pada struktur model Django, class admin, dan class trainer. Sementara itu, **polymorphism** dan **abstraction** juga ada, tetapi penggunaannya lebih terbatas dibanding dua pilar utama tadi.

## Class Diagram Lengkap

Berikut daftar 18 class yang dapat dimasukkan ke class diagram proyek ini. Notasi visibility yang dipakai:
- `+` = public
- `-` = private

Catatan: pada 18 class ini tidak ada member private yang didefinisikan secara eksplisit dengan underscore, sehingga hampir semua atribut dan method yang ditulis di bawah bersifat public.

### 1. `Brand`
- Atribut public:
	- `+ name`
	- `+ logo`
- Method public:
	- `+ __str__()`

### 2. `CarModel`
- Atribut public:
	- `+ brand`
	- `+ name`
- Method public:
	- `+ __str__()`

### 3. `CarDataset`
- Atribut public:
	- `+ brand`
	- `+ model`
	- `+ tahun`
	- `+ jarak_tempuh`
	- `+ transmisi`
	- `+ bahan_bakar`
	- `+ cc`
	- `+ harga`
	- `+ created_at`
	- `+ updated_at`
- Method public:
	- `+ __str__()`

### 5. `FileDataset`
- Atribut public:
	- `+ brand`
	- `+ file_excel`
	- `+ uploaded_at`
	- `+ file_size`
	- `+ row_count`
- Method public:
	- `+ __str__()`
	- `+ get_file_size_display()`
	- `+ save()`

### 6. `TrainingHistory`
- Atribut public:
	- `+ STATUS_CHOICES`
	- `+ brand`
	- `+ status`
	- `+ total_data`
	- `+ data_cleaned`
	- `+ data_removed`
	- `+ rmse`
	- `+ mae`
	- `+ r2_score`
	- `+ model_path`
	- `+ training_time`
	- `+ log_message`
	- `+ error_message`
	- `+ started_at`
	- `+ completed_at`
	- `+ trained_by`
- Method public:
	- `+ __str__()`
	- `+ get_accuracy_percentage()`

### 6. `CarDatasetAdmin`
- Atribut public:
	- tidak ada atribut class khusus yang didefinisikan
- Method public:
	- `+ has_module_permission()`
	- `+ has_add_permission()`
	- `+ has_change_permission()`
	- `+ has_delete_permission()`
	- `+ has_view_permission()`

### 7. `CarModelInline`
- Atribut public:
	- `+ model`
	- `+ extra`
	- `+ fields`
	- `+ can_delete`
- Method public:
	- tidak ada method khusus yang didefinisikan

### 8. `BrandAdmin`
- Atribut public:
	- `+ list_display`
	- `+ list_filter`
	- `+ inlines`
	- `+ list_per_page`
	- `+ actions`
- Method public:
	- `+ jumlah_model()`
	- `+ action_buttons()`
	- `+ get_urls()`
	- `+ delete_single_brand()`

### 9. `FileDatasetAdmin`
- Atribut public:
	- `+ list_display`
	- `+ list_filter`
	- `+ search_fields`
	- `+ readonly_fields`
	- `+ ordering`
	- `+ list_per_page`
	- `+ actions`
	- `+ fieldsets`
- Method public:
	- `+ file_name_display()`
	- `+ row_count_display()`
	- `+ action_buttons()`
	- `+ get_urls()`
	- `+ export_single_dataset()`
	- `+ delete_single_dataset()`
	- `+ save_model()`

### 12. `TrainModelDataset`
- Atribut public:
	- konfigurasi Meta:
		- `+ proxy`
		- `+ verbose_name`
		- `+ verbose_name_plural`
- Method public:
	- tidak ada method khusus yang didefinisikan

### 13. `TrainModelForm`
- Atribut public:
	- `+ brand`
- Method public:
	- `+ __init__()`

### 14. `TrainModelsAdmin`
- Atribut public:
	- `+ change_list_template`
- Method public:
	- `+ has_add_permission()`
	- `+ has_delete_permission()`
	- `+ has_change_permission()`
	- `+ changelist_view()`

### 15. `LinearModelTrainer`
- Atribut public:
	- `+ brand_name`
	- `+ model`
	- `+ metrics`
	- `+ log`
- Method public:
	- `+ __init__()`
	- `+ load_and_preprocess_data()`
	- `+ train_model()`
	- `+ save_model()`

### 16. `DashboardConfig`
- Atribut public:
	- `+ default_auto_field`
	- `+ name`
- Method public:
	- tidak ada method khusus yang didefinisikan

### 17. `PredictionConfig`
- Atribut public:
	- `+ default_auto_field`
	- `+ name`
- Method public:
	- `+ ready()`

### 18. `AuthApiConfig`
- Atribut public:
	- `+ default_auto_field`
	- `+ name`
- Method public:
	- tidak ada method khusus yang didefinisikan

### Ringkasan Class Diagram

Jika diringkas, class diagram lengkap project ini berisi 18 class dengan dominasi pada:
- model data Django di `prediction/models.py`
- class admin kustom di `prediction/admin.py`
- class training di `prediction/training_linear.py`
- konfigurasi app di `dashboard/apps.py`, `prediction/apps.py`, dan `users/apps.py`

Untuk dokumentasi skripsi, bagian yang paling penting tetap class model dan class trainer, karena dua kelompok itu paling kuat menunjukkan struktur OOP project.
