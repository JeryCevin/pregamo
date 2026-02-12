document.addEventListener('DOMContentLoaded', () => {
    
    const steps = document.querySelectorAll('.form-step');
    const form = document.getElementById('prediction-form');
    const modal = document.getElementById('predictionModal');
    
    // === FUNGSI NAVIGASI ===
    function goToStep(index) {
        steps.forEach((step, i) => {
            step.classList.toggle('active', i === index);
        });
    }

    document.querySelectorAll('.prev-btn').forEach(btn => {
        btn.addEventListener('click', () => goToStep(parseInt(btn.dataset.targetStep)));
    });

    // === FUNGSI PILIH KARTU (UMUM) ===
    // Digunakan untuk Merek, Model, Transmisi, dan Bahan Bakar
    function setupCardSelection(selector, inputId, callback) {
        const cards = document.querySelectorAll(selector);
        const input = document.getElementById(inputId);

        cards.forEach(card => {
            card.addEventListener('click', function() {
                // Reset seleksi di grup ini
                cards.forEach(c => c.classList.remove('selected'));
                // Pilih yang baru
                this.classList.add('selected');
                // Simpan data
                input.value = this.dataset.value;
                
                // Jalankan callback khusus
                if (callback) callback(this);
            });
        });
    }

    // 1. SETUP MEREK (Langsung pindah step)
    setupCardSelection('.brand-box', 'brand-input', (card) => {
        const brand = card.dataset.value;
        document.getElementById('selected-brand-title').textContent = brand;
        
        // Filter Model
        document.querySelectorAll('.model-group').forEach(group => {
            group.style.display = (group.dataset.brand === brand) ? 'grid' : 'none';
        });
        
        setTimeout(() => goToStep(1), 300);
    });

    // 2. SETUP MODEL (Langsung pindah step)
    setupCardSelection('.model-box', 'model-input', () => {
        setTimeout(() => goToStep(2), 300);
    });

    // 3. SETUP SPESIFIKASI (TRANSMISI & FUEL) - LOGIKA KHUSUS
    // Kita tidak langsung pindah step, tapi cek dulu apakah KEDUANYA sudah dipilih
    function checkStep3Completion() {
        const trans = document.getElementById('transmission-input').value;
        const fuel = document.getElementById('fuel-input').value;

        if (trans && fuel) {
            // Jika keduanya sudah terisi, update ringkasan dan pindah ke Step 4
            updateSummary();
            setTimeout(() => goToStep(3), 400); // Delay sedikit biar kelihatan terpilih
        }
    }

    setupCardSelection('.transmission-options .spec-box', 'transmission-input', checkStep3Completion);
    setupCardSelection('.fuel-options .spec-box', 'fuel-input', checkStep3Completion);


    // === UPDATE RINGKASAN (STEP 4) ===
    function updateSummary() {
        const brand = document.getElementById('brand-input').value;
        const model = document.getElementById('model-input').value;
        const trans = document.getElementById('transmission-input').value;
        const fuel = document.getElementById('fuel-input').value;
        
        // Update Gambar Logo
        const logoSrc = document.querySelector('.brand-box.selected img')?.src;
        if (logoSrc) document.getElementById('summary-image').src = logoSrc;

        // Update Teks
        document.getElementById('summary-text').innerHTML = 
            `${brand} ${model}<br>
             <span style="font-size: 0.9rem; color: var(--light-blue-accent)">${trans} • ${fuel}</span>`;
    }


    // === SUBMIT FORM ===
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const btn = document.querySelector('.submit-btn');
        const originalText = btn.innerHTML;
        
        btn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Memproses...';
        btn.disabled = true;

        console.log('=== DEBUG: Mengirim request prediksi ===');
        console.log('URL:', '/api/predict/run/');
        console.log('Form data:', new FormData(form));
        
        fetch('/api/predict/run/', { method: 'POST', body: new FormData(form) })
        .then(res => {
            console.log('Response status:', res.status);
            return res.json();
        })
        .then(data => {
            console.log('Response data:', data);
            btn.innerHTML = originalText;
            btn.disabled = false;
            
          if (data.error) return alert(data.error);

            // 1. Format Rupiah
            const formattedPrice = new Intl.NumberFormat('id-ID', {
                style: 'currency', currency: 'IDR', minimumFractionDigits: 0
            }).format(data.harga_prediksi);

            // 2. Tampilkan Harga Utama (Angka Besar)
            document.getElementById('predictedPrice').textContent = formattedPrice;
            
            // 3. ISI BOX KESIMPULAN (BARU)
            const conclusionElement = document.getElementById('conclusionText');
            
            // Ambil data mobil untuk dimasukkan ke kalimat (Opsional, biar keren)
            const brand = document.getElementById('brand-input').value;
            const model = document.getElementById('model-input').value;

            // Susun Kalimat
            conclusionElement.innerHTML = `
                Berdasarkan hasil perhitungan prediksi harga mobil 
                <span class="highlight-text">${brand} ${model}</span> 
                menggunakan algoritma <span class="highlight-text">Multiple Linear Regression</span>, 
                sistem mendapatkan estimasi harga pasar wajar sebesar 
                <span class="highlight-text">${formattedPrice}</span>. 
                Akurasi prediksi ini dipengaruhi oleh fitur kendaraan dan tren pasar saat ini.
            `;
            
            // Tampilkan Modal
            modal.style.display = 'flex';
        })
        .catch(err => {
            alert("Terjadi kesalahan sistem.");
            btn.disabled = false;
        });
    });

    // Tutup Modal
    const closeModal = () => modal.style.display = 'none';
    document.querySelector('.btn-selesai').addEventListener('click', closeModal);
    window.addEventListener('click', (e) => e.target === modal && closeModal());
});