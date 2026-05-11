# prediction/admin.py

from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Brand, CarModel, FileDataset, CarDataset  # TrainingHistory tidak dipakai
import pandas as pd
import os


# ============================================================================
# DEPRECATED MODEL - Hide from admin
# ============================================================================

@admin.register(CarDataset)
class CarDatasetAdmin(admin.ModelAdmin):
    """
    Admin untuk CarDataset (Legacy/Deprecated).
    Model ini tidak digunakan lagi, tapi perlu di-register untuk menghindari URL reverse error.
    """
    def has_module_permission(self, request):
        return False  # Hide dari admin sidebar
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_view_permission(self, request, obj=None):
        return False


# ============================================================================
# ADMIN UNTUK BRAND & CAR MODELS
# ============================================================================


# Inline untuk menambah Car Model langsung dari halaman Brand
class CarModelInline(admin.TabularInline):
    model = CarModel
    extra = 1  # Tampilkan 1 form kosong untuk input cepat
    fields = ['name']
    can_delete = True  # Bisa hapus inline

# Admin untuk Brand dengan inline Car Models
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'logo', 'jumlah_model', 'action_buttons']
    list_filter = ['name']
    inlines = [CarModelInline]
    list_per_page = 20
    
    # Disable bulk actions
    actions = None
    
    # Custom display untuk menampilkan jumlah model per brand
    @admin.display(description='Jumlah Model')
    def jumlah_model(self, obj):
        return obj.models.count()
    
    @admin.display(description='Aksi')
    def action_buttons(self, obj):
        """Tombol aksi Edit dan Delete untuk setiap row"""
        return format_html(
            '<a class="button" href="{}" style="background: #417690; color: white; padding: 8px 12px; '
            'border-radius: 4px; text-decoration: none; margin-right: 5px; display: inline-block;">'
            'Edit</a>'
            '<a class="button" href="{}" onclick="return confirm(\'Yakin ingin menghapus brand ini?\');" '
            'style="background: #dc3545; color: white; padding: 8px 12px; border-radius: 4px; '
            'text-decoration: none; display: inline-block;">Delete</a>',
            reverse('admin:prediction_brand_change', args=[obj.id]),
            reverse('admin:prediction_brand_delete_custom', args=[obj.id])
        )
    
    # Custom URLs untuk action buttons
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:brand_id>/delete-custom/', self.admin_site.admin_view(self.delete_single_brand), name='prediction_brand_delete_custom'),
        ]
        return custom_urls + urls
    
    def delete_single_brand(self, request, brand_id):
        """Delete single brand dari button di row"""
        try:
            brand = Brand.objects.get(id=brand_id)
            brand_name = brand.name
            brand.delete()
            messages.success(request, f'✅ Brand {brand_name} berhasil dihapus!')
        except Brand.DoesNotExist:
            messages.error(request, '❌ Brand tidak ditemukan!')
        except Exception as e:
            messages.error(request, f'❌ Error delete: {str(e)}')
        
        return redirect('admin:prediction_brand_changelist')


# ============================================================================
# ADMIN UNTUK FILE-BASED WORKFLOW (NEW)
# ============================================================================

@admin.register(FileDataset)
class FileDatasetAdmin(admin.ModelAdmin):
    """
    Admin untuk manage upload file Excel dataset per brand.
    Workflow baru: Upload File → Export/Delete via Actions.
    """
    
    list_display = [
        'brand',
        'file_name_display',
        'row_count_display',
        'uploaded_at',
        'action_buttons',
    ]
    
    list_filter = [
        'brand',
        'uploaded_at',
    ]
    
    search_fields = [
        'brand__name',
    ]
    
    readonly_fields = ['uploaded_at', 'file_size', 'row_count']
    
    ordering = ['-uploaded_at']
    list_per_page = 25
    
    # Disable bulk actions (gunakan button per row)
    actions = None
    
    fieldsets = (
        ('Upload Dataset', {
            'fields': ('brand', 'file_excel')
        }),
        ('Informasi File', {
            'fields': ('uploaded_at', 'file_size', 'row_count'),
            'classes': ('collapse',)
        }),
    )
    
    # Custom display methods
    @admin.display(description='Nama File')
    def file_name_display(self, obj):
        """Tampilkan nama file sebagai text (non-clickable)"""
        filename = os.path.basename(obj.file_excel.name)
        return format_html('📄 {}', filename)
    
    @admin.display(description='Jumlah Data')
    def row_count_display(self, obj):
        """Tampilkan jumlah baris data"""
        if obj.row_count > 0:
            return format_html('<strong>{}</strong> baris', obj.row_count)
        return '-'
    
    @admin.display(description='Aksi')
    def action_buttons(self, obj):
        """Tombol aksi Edit, Export dan Delete untuk setiap row"""
        return format_html(
            '<a class="button" href="{}" style="background: #007bff; color: white; padding: 8px 12px; '
            'border-radius: 4px; text-decoration: none; margin-right: 5px; display: inline-block;">'
            'Edit</a>'
            '<a class="button" href="{}" style="background: #28a745; color: white; padding: 8px 12px; '
            'border-radius: 4px; text-decoration: none; margin-right: 5px; display: inline-block;">'
            'Export</a>'
            '<a class="button" href="{}" onclick="return confirm(\'Yakin ingin menghapus dataset ini?\');" '
            'style="background: #dc3545; color: white; padding: 8px 12px; border-radius: 4px; '
            'text-decoration: none; display: inline-block;">Delete</a>',
            reverse('admin:prediction_filedataset_change', args=[obj.id]),
            reverse('admin:prediction_filedataset_export', args=[obj.id]),
            reverse('admin:prediction_filedataset_delete', args=[obj.id])
        )
    
    # Custom URLs untuk action buttons
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:dataset_id>/export/', self.admin_site.admin_view(self.export_single_dataset), name='prediction_filedataset_export'),
            path('<int:dataset_id>/delete/', self.admin_site.admin_view(self.delete_single_dataset), name='prediction_filedataset_delete'),
        ]
        return custom_urls + urls
    
    def export_single_dataset(self, request, dataset_id):
        """Export single dataset dari button di row"""
        try:
            dataset = FileDataset.objects.get(id=dataset_id)
            
            # Baca file Excel
            file_path = dataset.file_excel.path
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.xlsx':
                df = pd.read_excel(file_path, engine='openpyxl')
            elif file_ext == '.xls':
                df = pd.read_excel(file_path, engine='xlrd')
            elif file_ext == '.csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path, engine='openpyxl')
            
            # Create HTTP response dengan Excel file
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{dataset.brand.name}_dataset.xlsx"'
            
            # Write dataframe to response
            with pd.ExcelWriter(response, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Dataset')
            
            return response
            
        except FileDataset.DoesNotExist:
            messages.error(request, '❌ Dataset tidak ditemukan!')
            return redirect('admin:prediction_filedataset_changelist')
        except Exception as e:
            messages.error(request, f'❌ Error export: {str(e)}')
            return redirect('admin:prediction_filedataset_changelist')
    
    def delete_single_dataset(self, request, dataset_id):
        """Delete single dataset dari button di row"""
        try:
            dataset = FileDataset.objects.get(id=dataset_id)
            brand_name = dataset.brand.name
            dataset.delete()
            messages.success(request, f'✅ Dataset {brand_name} berhasil dihapus!')
        except FileDataset.DoesNotExist:
            messages.error(request, '❌ Dataset tidak ditemukan!')
        except Exception as e:
            messages.error(request, f'❌ Error delete: {str(e)}')
        
        return redirect('admin:prediction_filedataset_changelist')
    
    def save_model(self, request, obj, form, change):
        """Override save untuk hitung row count dari Excel"""
        super().save_model(request, obj, form, change)
        
        # Hitung jumlah baris dari file Excel
        if obj.file_excel:
            try:
                # Deteksi engine berdasarkan ekstensi file
                file_path = obj.file_excel.path
                file_ext = os.path.splitext(file_path)[1].lower()
                
                if file_ext == '.xlsx':
                    df = pd.read_excel(file_path, engine='openpyxl')
                elif file_ext == '.xls':
                    df = pd.read_excel(file_path, engine='xlrd')
                elif file_ext == '.csv':
                    df = pd.read_csv(file_path)
                else:
                    # Default openpyxl untuk format modern
                    df = pd.read_excel(file_path, engine='openpyxl')
                
                obj.row_count = len(df)
                obj.save(update_fields=['row_count'])
                messages.success(request, f"✅ File berhasil diupload! Ditemukan {len(df)} baris data.")
            except Exception as e:
                messages.warning(request, f"⚠️ File diupload tapi tidak bisa menghitung jumlah baris: {str(e)}")


# ============================================================================
# TRAIN MODELS 
# ============================================================================

class TrainModelDataset(FileDataset):
    """Proxy model untuk Train Models view - menggunakan FileDataset sebagai base"""
    class Meta:
        proxy = True
        verbose_name = "Train Model"
        verbose_name_plural = "Train Models"

# Form untuk Train Models
class TrainModelForm(forms.Form):
    """Form sederhana untuk pilih brand untuk training"""
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.filter(file_datasets__isnull=False).distinct(),
        label='Pilih Brand',
        required=True,
        empty_label='---------',
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add dataset count to label
        brand_qs = Brand.objects.filter(file_datasets__isnull=False).distinct()
        choices = [('', '---------')]
        for brand in brand_qs:
            count = FileDataset.objects.filter(brand=brand).count()
            choices.append((brand.id, f'{brand.name} ({count} dataset)'))
        self.fields['brand'].choices = choices


@admin.register(TrainModelDataset)
class TrainModelsAdmin(admin.ModelAdmin):
    """
    Admin untuk Train Models - form sederhana pilih brand dan train.
    Menggunakan mekanisme bawaan Django admin.
    """
    
    change_list_template = 'admin/Train_models.html'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def changelist_view(self, request, extra_context=None):
        """Override changelist untuk tampilan form sederhana"""
        
        # Handle POST request (train model)
        if request.method == 'POST':
            form = TrainModelForm(request.POST)
            if form.is_valid():
                brand = form.cleaned_data['brand']
                try:
                    # Cari dataset untuk brand ini
                    dataset = FileDataset.objects.filter(brand=brand).order_by('-uploaded_at').first()
                    
                    if dataset:
                        # Training menggunakan modul training_linear
                        from .training_linear import train_from_file
                        
                        result = train_from_file(dataset.id)
                        
                        if result['success']:
                            metrics = result['metrics']
                            messages.success(
                                request,
                                mark_safe(
                                    f"✅ <strong>Training Berhasil!</strong><br>"
                                    f"Brand: <strong>{brand.name}</strong><br>"
                                    f"R² Score: <strong>{metrics['accuracy_percentage']:.2f}%</strong><br>"
                                    f"RMSE: Rp {metrics['rmse']:,.0f} (<strong>{metrics['rmse_percentage']:.2f}%</strong>)<br>"
                                    f"Waktu: {result['training_time']:.2f} detik"
                                )
                            )
                        else:
                            messages.error(request, f"❌ Training gagal: {result['message']}")
                    else:
                        messages.error(request, f'❌ Tidak ada dataset untuk brand {brand.name}!')
                        
                except Exception as e:
                    messages.error(request, f'❌ Error training: {str(e)}')
                
                return redirect('admin:prediction_trainmodeldataset_changelist')
            else:
                messages.error(request, '❌ Pilih brand terlebih dahulu!')
        else:
            form = TrainModelForm()
        
        # Context untuk template bawaan admin
        context = {
            'form': form,
            'title': 'Train Models',
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
        }
        
        extra_context = extra_context or {}
        context.update(extra_context)
        
        return super().changelist_view(request, extra_context=context)

