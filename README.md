# Tugas Besar IF3130 - jaringan-komputer-j-nya-jarkom

Repositori ini berisi cara mensimulasikan koneksi TCP melalui soket UDP. 
Di dalamnya terdapat server dan klien sederhana yang memungkinkan server untuk mengirim file kepada satu atau beberapa klien.
Implementasi ini tidak menggunakan _library_ tambahan selain yang sudah tersedia secara bawaan.

## _Requirement_
- Install Python (versi 3) 

## Cara menjalankan
1. Jalankan _server_ dengan _command_ dibawah ini pada terminal:
```sh
python3 server.py 3002 .gitignore
```
2. Jalankan _client_ dengan _command_ dibawah ini pada terminal yang berbeda:
```sh
python3 client.py 3000 3002 client-out
```

# Member
* 13521093 - Akbar Maulana Ridho
* 13521045 - Fakhri Muhammad Mahendra
* 13521151 - Vanessa Rebecca Wiyono
  
