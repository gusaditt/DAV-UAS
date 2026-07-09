import sys
import pandas as pd
from pathlib import Path

def explore_dataset(file_path: str, output_path: str):
    """
    Explores the KopiSeru dataset and writes a comprehensive summary to output_path.
    """
    path = Path(file_path)
    if not path.exists():
        print(f"Error: Dataset file '{file_path}' not found.")
        sys.exit(1)
        
    print(f"Loading dataset from {file_path}...")
    df = pd.read_excel(path)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("       KOPISERU DATASET EXPLORATION & SUMMARY STATISTICS\n")
        f.write("=" * 60 + "\n\n")
        
        # 1. Basic Info
        f.write("1. METADATA RINGKAS\n")
        f.write("-" * 30 + "\n")
        f.write(f"Nama Berkas      : {path.name}\n")
        f.write(f"Ukuran Berkas    : {path.stat().st_size / (1024*1024):.2f} MB\n")
        f.write(f"Jumlah Baris     : {df.shape[0]:,}\n")
        f.write(f"Jumlah Kolom     : {df.shape[1]}\n\n")
        
        # 2. Columns list & Data types
        f.write("2. DAFTAR KOLOM DAN TIPE DATA\n")
        f.write("-" * 30 + "\n")
        for i, (col, dtype) in enumerate(zip(df.columns, df.dtypes), 1):
            null_count = df[col].isnull().sum()
            null_pct = (null_count / len(df)) * 100
            f.write(f" {i:2d}. {col:<25} : {str(dtype):<15} (Nulls: {null_count:,} / {null_pct:.2f}%)\n")
        f.write("\n")
        
        # 3. Descriptive Stats for Numeric Columns
        f.write("3. STATISTIK DESKRIPTIF (KOLOM NUMERIK)\n")
        f.write("-" * 30 + "\n")
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        if numeric_cols:
            desc = df[numeric_cols].describe().transpose()
            f.write(desc.to_string())
            f.write("\n\n")
        else:
            f.write("Tidak ada kolom numerik.\n\n")
            
        # 4. Value counts for Categorical Columns
        f.write("4. DISTRIBUSI KATEGORI UTAMA\n")
        f.write("-" * 30 + "\n")
        cat_cols = ["branch_type", "promo_active", "promo_type", "is_weekend", "top_selling_category"]
        for col in cat_cols:
            if col in df.columns:
                f.write(f"\nKolom: {col}\n")
                vc = df[col].value_counts(dropna=False)
                for val, count in vc.items():
                    pct = (count / len(df)) * 100
                    f.write(f"  - {str(val):<25} : {count:5,} ({pct:.2f}%)\n")
        f.write("\n")
        
        # 5. Data Completeness check
        f.write("5. KESIMPULAN KUALITAS DATA\n")
        f.write("-" * 30 + "\n")
        total_nulls = df.isnull().sum().sum()
        f.write(f"Total missing values (nulls) di seluruh dataset: {total_nulls:,}\n")
        if total_nulls == 0:
            f.write("Status: Data Bersih (Tidak ada missing values).\n")
        else:
            f.write("Status: Perlu pembersihan data sebelum visualisasi.\n")
            
    print(f"Exploration completed successfully. Results saved to '{output_path}'.")

if __name__ == "__main__":
    explore_dataset("coffe_shop_final.xlsx", "data_info.txt")
