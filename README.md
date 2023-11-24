# Tubes-IF3140

## Usage

1. Clone repository https://github.com/Enliven26/Tubes-IF3140.  
3. Pindah ke folder repository  
```bash
cd local/path/to/Tubes-IF3140
```
2. Install virtualenv pada mesin lokal.  
```bash
pip install virtualenv
```
3. Buat virtual environment.
```bash
python -m venv venv
```
4. Aktifkan virtual environment.  
```bash
venv\Scripts\activate
```
5. Install semua package yang diperlukan.    
```bash
pip install -r requirements.txt
```
6. Apabila ada melakukan instalasi package baru, pastikan melakukan update ke requirements.txt.  
```bash
pip freeze > requirements.txt
```

7. Pindah ke folder src untuk menjalankan program.  
```bash
cd src
```

8. Deactivate virtual environment jika tidak diperlukan lagi.  
```bash
deactivate
```