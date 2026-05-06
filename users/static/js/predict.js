document.addEventListener('DOMContentLoaded', () => {
    const steps = document.querySelectorAll('.form-step');
    const form = document.getElementById('prediction-form');
    const modal = document.getElementById('predictionModal');

    // === FUNGSI NAVIGASI ===
    function goToStep(index) {
        steps.forEach((step, i) => step.classList.toggle('active', i === index));
        if (index === 3) updateSummary();
    }

    document.querySelectorAll('.prev-btn').forEach(btn => 
        btn.addEventListener('click', () => goToStep(parseInt(btn.dataset.targetStep)))
    );

    // === FUNGSI PILIH KARTU (UMUM) ===
    function setupCardSelection(selector, inputId, callback) {
        const cards = document.querySelectorAll(selector);
        const input = document.getElementById(inputId);

        cards.forEach(card => {
            card.addEventListener('click', function() {
                cards.forEach(c => c.classList.remove('selected'));
                this.classList.add('selected');
                if (input) input.value = this.dataset.value || '';
                if (callback) callback(this);
            });
        });
    }

    // 1. Pilih Brand -> Munculkan Model -> Pindah Step 2
    setupCardSelection('.brand-box', 'brand-input', (card) => {
        const brand = card.dataset.value;
        const titleEl = document.getElementById('selected-brand-title');
        if (titleEl) titleEl.textContent = brand;
        
        document.querySelectorAll('.model-group').forEach(group => {
            group.style.display = (group.dataset.brand === brand) ? 'grid' : 'none';
        });
        setTimeout(() => goToStep(1), 300);
    });

    // 2. Pilih Model -> Pindah Step 3
    setupCardSelection('.model-box', 'model-input', () => setTimeout(() => goToStep(2), 300));

    // 3. Pilih Transmisi & Bahan Bakar -> Pindah Step 4 jika keduanya sudah diisi
    function checkStep3Completion() {
        const trans = document.getElementById('transmission-input')?.value;
        const fuel = document.getElementById('fuel-input')?.value;
        if (trans && fuel) {
            updateSummary();
            setTimeout(() => goToStep(3), 300);
        }
    }

    setupCardSelection('.transmission-options .spec-box', 'transmission-input', checkStep3Completion);
    setupCardSelection('.fuel-options .spec-box', 'fuel-input', checkStep3Completion);

    // === UPDATE RINGKASAN DI STEP 4 ===
    function updateSummary() {
        const brand = document.getElementById('brand-input')?.value || '';
        const model = document.getElementById('model-input')?.value || '';
        const trans = document.getElementById('transmission-input')?.value || '';
        const fuel = document.getElementById('fuel-input')?.value || '';

        const logoSrc = document.querySelector('.brand-box.selected img')?.src;
        const summaryImg = document.getElementById('summary-image');
        if (logoSrc && summaryImg) summaryImg.src = logoSrc;

        const summaryText = document.getElementById('summary-text');
        if (summaryText) summaryText.innerHTML = `${brand} ${model}<br><span style="font-size:0.9rem;color:var(--light-blue-accent)">${trans} • ${fuel}</span>`;
    }

    // === SUBMIT FORM PREDIKSI ===
    form?.addEventListener('submit', function(e) {
        e.preventDefault();
        const btn = document.querySelector('.submit-btn');
        if (!btn) return;
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Memproses...';
        btn.disabled = true;

fetch('/api/predict/run/', { method: 'POST', body: new FormData(form) })
        .then(res => res.json())
        .then(data => {
            btn.innerHTML = originalText;
            btn.disabled = false;
            if (data.error) return alert(data.error);

            // 1. PEMBULATAN HARGA (Dibulatkan ke ratusan ribu terdekat)
            const rawPrice = data.harga_prediksi;
            const roundedPrice = Math.round(rawPrice / 100000) * 100000;
            const formattedPrice = new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(roundedPrice);

            const priceEl = document.getElementById('predictedPrice'); 
            if (priceEl) priceEl.textContent = formattedPrice;

            // 2. RENTANG HARGA (TOLERANSI)
            // Jika backend punya data.harga_min/max, gunakan itu. Jika tidak, buat toleransi otomatis ± 5%
            let minRaw = data.harga_min !== undefined ? data.harga_min : (rawPrice * 0.95);
            let maxRaw = data.harga_max !== undefined ? data.harga_max : (rawPrice * 1.05);
            
            // Bulatkan juga rentangnya
            const minRounded = Math.round(minRaw / 100000) * 100000;
            const maxRounded = Math.round(maxRaw / 100000) * 100000;

            const formattedMin = new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(minRounded);
            const formattedMax = new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(maxRounded);

            const rangeEl = document.getElementById('predictedRange');
            if (rangeEl) {
                rangeEl.innerHTML = `Estimasi Rentang Pasar:<br><span class="highlight-range">${formattedMin} - ${formattedMax}</span>`;
            }

            // 3. TAMPILKAN RINGKASAN INPUT LENGKAP
            const b = document.getElementById('brand-input')?.value || '';
            const m = document.getElementById('model-input')?.value || '';
            const t = document.getElementById('transmission-input')?.value || '';
            const y = document.getElementById('year')?.value || '';
            const mil = document.getElementById('mileage')?.value || '';
            const c = document.getElementById('cc')?.value || '';
            
            const formattedMileage = new Intl.NumberFormat('id-ID').format(mil);
            const detailString = `(Tahun ${y} | ${formattedMileage} km | ${c} cc | ${t})`;

            const modalText = document.getElementById('modal-summary-text');
            if (modalText) {
                modalText.innerHTML = `<strong>${b} ${m}</strong><br><span class="modal-detail-sub">${detailString}</span>`;
            }

            // Copy gambar logo
            const srcImg = document.getElementById('summary-image');
            const modalImg = document.getElementById('modal-summary-image');
            if (modalImg && srcImg) modalImg.src = srcImg.src;

            // Teks Kesimpulan
            const conclusionElement = document.getElementById('conclusionText');
            if (conclusionElement) {
                conclusionElement.innerHTML = `Berdasarkan hasil perhitungan prediksi harga menggunakan algoritma <span class="highlight-text">Multiple Linear Regression</span>, sistem mendapatkan estimasi harga pasar wajar dengan nilai tengah sebesar <span class="highlight-text">${formattedPrice}</span>.`;
            }

            modal.style.display = 'flex';
        })
        .catch(err => {
            alert('Terjadi kesalahan saat menghubungi server.');
            btn.disabled = false;
            btn.innerHTML = originalText;
        });
    });

    // === TUTUP MODAL & REFRESH LANGSUNG KE FORM ===
    document.querySelectorAll('.btn-selesai').forEach(b => {
        b.addEventListener('click', () => {
            // Refresh dan otomatis scroll ke bagian id="prediksi"
            window.location.href = window.location.pathname + '#prediksi';
            window.location.reload(); 
        });
    });
});