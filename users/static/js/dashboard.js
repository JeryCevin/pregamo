
        // Menjalankan script setelah seluruh struktur HTML selesai dimuat
        document.addEventListener('DOMContentLoaded', () => {
            
            // 1. Mencari elemen span yang menampilkan email berdasarkan class-nya
            const userEmailElement = document.querySelector('.user-email');

            // Lanjutkan hanya jika elemennya ditemukan
            if (userEmailElement) {
                // 2. Mengambil seluruh teks di dalamnya
                // Contoh: "Selamat Datang, kenokecapzzz12@gmail.com"
                const fullText = userEmailElement.textContent; 

                // 3. Memisahkan teks untuk mendapatkan alamat emailnya saja
                const email = fullText.split(', ')[1]; 
                
                // Lanjutkan hanya jika email berhasil diekstrak
                if (email) {
                    // 4. Memproses email: ambil bagian sebelum @ dan hapus angka
                    const usernamePart = email.split('@')[0];
                    const cleanUsername = usernamePart.replace(/\d/g, ''); // Menghapus semua digit

                    // 5. Mengganti teks di elemen span dengan nama yang sudah bersih
                    userEmailElement.textContent = `Selamat Datang, ${cleanUsername}`;
                }
            }
        });
