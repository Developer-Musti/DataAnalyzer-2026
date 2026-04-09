import customtkinter as ctk
from tkinter import filedialog, messagebox
import csv
import os
from collections import Counter
import statistics

# Tema ayarları
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Matplotlib kontrolü
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

class DataAnalyzer:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("DataAnalyzer - CSV Analyzer")
        self.window.geometry("1200x700")
        self.window.iconbitmap("Icon.ico")
        
        # Değişkenler
        self.data = []  # Tüm veriler (list of lists)
        self.headers = []  # Sütun başlıkları
        self.file_path = None
        self.column_types = {}  # Sütun tipleri
        
        self.setup_ui()
        
        # Matplotlib kontrolü
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showwarning("Uyarı", 
                "Matplotlib kütüphanesi bulunamadı!\n\n"
                "Grafik özellikleri devre dışı.\n"
                "Kurmak için: pip install matplotlib")
        
    def setup_ui(self):
        # Ana frame
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Sol panel - Kontroller
        self.left_panel = ctk.CTkFrame(self.main_frame, width=300)
        self.left_panel.pack(side="left", fill="y", padx=(0, 10))
        self.left_panel.pack_propagate(False)
        
        # Başlık
        title_label = ctk.CTkLabel(
            self.left_panel, 
            text="DataAnalyzer", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        subtitle = ctk.CTkLabel(
            self.left_panel,
            text="CSV Veri Analiz Aracı",
            font=ctk.CTkFont(size=12)
        )
        subtitle.pack(pady=(0, 10))
        
        # Dosya yükleme butonu
        self.load_btn = ctk.CTkButton(
            self.left_panel,
            text="📂 CSV Dosyası Yükle",
            command=self.load_file,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.load_btn.pack(pady=10, padx=20, fill="x")
        
        # Dosya bilgisi
        self.file_info = ctk.CTkLabel(
            self.left_panel,
            text="Henüz dosya yüklenmedi",
            font=ctk.CTkFont(size=12),
            wraplength=250
        )
        self.file_info.pack(pady=5)
        
        # Ayraç
        ctk.CTkFrame(self.left_panel, height=2).pack(fill="x", pady=15, padx=20)
        
        # Analiz seçenekleri
        options_label = ctk.CTkLabel(
            self.left_panel,
            text="Analiz Seçenekleri",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        options_label.pack(pady=10)
        
        # İstatistikler butonu
        self.stats_btn = ctk.CTkButton(
            self.left_panel,
            text="📊 Temel İstatistikler",
            command=self.show_statistics,
            state="disabled",
            height=35
        )
        self.stats_btn.pack(pady=5, padx=20, fill="x")
        
        # Sütun analizi
        self.column_btn = ctk.CTkButton(
            self.left_panel,
            text="📋 Sütun Analizi",
            command=self.show_column_analysis,
            state="disabled",
            height=35
        )
        self.column_btn.pack(pady=5, padx=20, fill="x")
        
        # Frekans analizi
        self.freq_btn = ctk.CTkButton(
            self.left_panel,
            text="🔢 Frekans Analizi",
            command=self.show_frequency_analysis,
            state="disabled",
            height=35
        )
        self.freq_btn.pack(pady=5, padx=20, fill="x")
        
        # Grafik butonları
        if MATPLOTLIB_AVAILABLE:
            self.hist_btn = ctk.CTkButton(
                self.left_panel,
                text="📈 Histogram",
                command=self.show_histogram,
                state="disabled",
                height=35
            )
            self.hist_btn.pack(pady=5, padx=20, fill="x")
            
            self.bar_btn = ctk.CTkButton(
                self.left_panel,
                text="📊 Bar Grafik",
                command=self.show_bar_chart,
                state="disabled",
                height=35
            )
            self.bar_btn.pack(pady=5, padx=20, fill="x")
        else:
            self.hist_btn = ctk.CTkButton(
                self.left_panel,
                text="📈 Histogram (Matplotlib yok)",
                state="disabled",
                height=35
            )
            self.hist_btn.pack(pady=5, padx=20, fill="x")
            
            self.bar_btn = ctk.CTkButton(
                self.left_panel,
                text="📊 Bar Grafik (Matplotlib yok)",
                state="disabled",
                height=35
            )
            self.bar_btn.pack(pady=5, padx=20, fill="x")
        
        # Ayraç
        ctk.CTkFrame(self.left_panel, height=2).pack(fill="x", pady=15, padx=20)
        
        # Önizleme ayarları
        preview_label = ctk.CTkLabel(
            self.left_panel,
            text="Önizleme Satır Sayısı",
            font=ctk.CTkFont(size=12)
        )
        preview_label.pack(pady=5)
        
        self.preview_rows = ctk.CTkOptionMenu(
            self.left_panel,
            values=["5", "10", "20", "50", "100"],
            command=self.update_preview
        )
        self.preview_rows.set("10")
        self.preview_rows.pack(pady=5, padx=20)
        
        # Sağ panel - Görüntüleme alanı
        self.right_panel = ctk.CTkFrame(self.main_frame)
        self.right_panel.pack(side="right", fill="both", expand=True)
        
        # Tab view
        self.tabview = ctk.CTkTabview(self.right_panel)
        self.tabview.pack(fill="both", expand=True)
        
        # Tablar
        self.tabview.add("Veri Önizleme")
        self.tabview.add("Analiz Sonuçları")
        if MATPLOTLIB_AVAILABLE:
            self.tabview.add("Grafik")
        
        # Veri önizleme textbox
        self.preview_text = ctk.CTkTextbox(
            self.tabview.tab("Veri Önizleme"),
            font=ctk.CTkFont(family="Courier", size=11)
        )
        self.preview_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Analiz sonuçları textbox
        self.results_text = ctk.CTkTextbox(
            self.tabview.tab("Analiz Sonuçları"),
            font=ctk.CTkFont(family="Courier", size=11)
        )
        self.results_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Grafik frame
        if MATPLOTLIB_AVAILABLE:
            self.graph_frame = ctk.CTkFrame(self.tabview.tab("Grafik"))
            self.graph_frame.pack(fill="both", expand=True)
        
        # Status bar
        self.status_bar = ctk.CTkLabel(
            self.window,
            text="Hazır - CSV dosyası yükleyin",
            anchor="w",
            font=ctk.CTkFont(size=11)
        )
        self.status_bar.pack(side="bottom", fill="x", padx=10, pady=5)
    
    def detect_delimiter(self, file_path):
        """CSV ayracını otomatik tespit et"""
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            
        # Yaygın ayraçları kontrol et
        delimiters = [',', ';', '\t', '|']
        counts = {d: first_line.count(d) for d in delimiters}
        
        # En çok kullanılan ayracı seç
        best_delimiter = max(counts, key=counts.get)
        
        if counts[best_delimiter] == 0:
            return ','  # Varsayılan
        return best_delimiter
    
    def detect_column_types(self):
        """Sütunların sayısal mı yoksa metin mi olduğunu tespit et"""
        self.column_types = {}
        
        for col_idx, header in enumerate(self.headers):
            is_numeric = True
            numeric_count = 0
            total_count = 0
            
            for row in self.data[:min(100, len(self.data))]:  # İlk 100 satırı kontrol et
                if col_idx < len(row) and row[col_idx].strip():
                    total_count += 1
                    try:
                        float(row[col_idx].replace(',', '.'))
                        numeric_count += 1
                    except:
                        pass
            
            # %90'dan fazlası sayısal ise numeric kabul et
            if total_count > 0 and (numeric_count / total_count) > 0.9:
                self.column_types[col_idx] = 'numeric'
            else:
                self.column_types[col_idx] = 'text'
    
    def get_numeric_values(self, col_idx):
        """Sütundaki sayısal değerleri döndür"""
        values = []
        for row in self.data:
            if col_idx < len(row) and row[col_idx].strip():
                try:
                    val = float(row[col_idx].replace(',', '.'))
                    values.append(val)
                except:
                    pass
        return values
    
    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="CSV dosyası seçin",
            filetypes=[
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.status_bar.configure(text=f"Yükleniyor: {os.path.basename(file_path)}")
                self.window.update()
                
                # Ayracı tespit et
                delimiter = self.detect_delimiter(file_path)
                
                # CSV'yi oku
                self.data = []
                self.headers = []
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter=delimiter)
                    
                    # Başlıkları al
                    try:
                        self.headers = next(reader)
                    except StopIteration:
                        messagebox.showerror("Hata", "Dosya boş!")
                        return
                    
                    # Verileri al
                    for row in reader:
                        self.data.append(row)
                
                self.file_path = file_path
                
                # Sütun tiplerini tespit et
                self.detect_column_types()
                
                # Butonları aktif et
                self.stats_btn.configure(state="normal")
                self.column_btn.configure(state="normal")
                self.freq_btn.configure(state="normal")
                
                if MATPLOTLIB_AVAILABLE:
                    # Sayısal sütun varsa grafik butonlarını aktif et
                    if any(t == 'numeric' for t in self.column_types.values()):
                        self.hist_btn.configure(state="normal")
                    
                    # Kategorik sütun varsa bar grafiği aktif et
                    if any(t == 'text' for t in self.column_types.values()):
                        self.bar_btn.configure(state="normal")
                
                # Dosya bilgisini güncelle
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path) / 1024  # KB
                
                info_text = f"Dosya: {file_name}\n"
                info_text += f"Satır: {len(self.data):,}\n"
                info_text += f"Sütun: {len(self.headers)}\n"
                info_text += f"Boyut: {file_size:.1f} KB\n"
                info_text += f"Ayraç: '{delimiter}'\n"
                info_text += f"Sayısal Sütun: {sum(1 for t in self.column_types.values() if t == 'numeric')}"
                
                self.file_info.configure(text=info_text)
                
                # Önizlemeyi güncelle
                self.update_preview()
                
                self.status_bar.configure(text=f"✓ Yüklendi: {file_name} ({len(self.data):,} satır)")
                
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya yüklenirken hata oluştu:\n{str(e)}")
                self.status_bar.configure(text="Hata oluştu")
    
    def update_preview(self, choice=None):
        if self.data:
            try:
                n_rows = min(int(self.preview_rows.get()), len(self.data))
                
                preview_text = f"=== VERİ ÖNİZLEME (İlk {n_rows} satır) ===\n\n"
                
                # Başlıklar
                preview_text += " | ".join(self.headers) + "\n"
                preview_text += "-" * 100 + "\n"
                
                # Veriler
                for i in range(n_rows):
                    row = self.data[i]
                    preview_text += " | ".join(str(cell) for cell in row) + "\n"
                
                preview_text += f"\n=== SÜTUN BİLGİLERİ ===\n\n"
                
                for idx, header in enumerate(self.headers):
                    col_type = self.column_types.get(idx, 'text')
                    non_empty = sum(1 for row in self.data if idx < len(row) and row[idx].strip())
                    
                    preview_text += f"{header}: {col_type} | "
                    preview_text += f"Dolu: {non_empty}/{len(self.data)} | "
                    
                    if col_type == 'numeric':
                        values = self.get_numeric_values(idx)
                        if values:
                            preview_text += f"Min: {min(values):.2f} | Max: {max(values):.2f}"
                    
                    preview_text += "\n"
                
                self.preview_text.delete("1.0", "end")
                self.preview_text.insert("1.0", preview_text)
                
            except Exception as e:
                messagebox.showerror("Hata", f"Önizleme hatası: {str(e)}")
    
    def show_statistics(self):
        if not self.data:
            return
            
        self.tabview.set("Analiz Sonuçları")
        
        results = "=== TEMEL İSTATİSTİKLER ===\n\n"
        
        # Genel bilgiler
        results += f"Toplam Satır: {len(self.data):,}\n"
        results += f"Toplam Sütun: {len(self.headers)}\n\n"
        
        # Her sütun için istatistikler
        for idx, header in enumerate(self.headers):
            if self.column_types.get(idx) == 'numeric':
                values = self.get_numeric_values(idx)
                
                if values:
                    results += f"\n{header}:\n"
                    results += f"  - Değer Sayısı: {len(values):,}\n"
                    results += f"  - Eksik Değer: {len(self.data) - len(values):,}\n"
                    results += f"  - Ortalama: {statistics.mean(values):.2f}\n"
                    results += f"  - Medyan: {statistics.median(values):.2f}\n"
                    results += f"  - Min: {min(values):.2f}\n"
                    results += f"  - Max: {max(values):.2f}\n"
                    
                    if len(values) > 1:
                        results += f"  - Std Sapma: {statistics.stdev(values):.2f}\n"
        
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", results)
        self.status_bar.configure(text="İstatistikler hesaplandı")
    
    def show_column_analysis(self):
        if not self.data:
            return
            
        self.tabview.set("Analiz Sonuçları")
        
        # Sütun seçimi
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Sütun Seç")
        dialog.geometry("300x400")
        
        ctk.CTkLabel(dialog, text="Analiz edilecek sütunu seçin:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        selected_col = ctk.StringVar(value=self.headers[0])
        
        for header in self.headers:
            ctk.CTkRadioButton(
                dialog,
                text=header,
                variable=selected_col,
                value=header
            ).pack(pady=5, padx=20, anchor="w")
        
        def analyze_column():
            col_name = selected_col.get()
            col_idx = self.headers.index(col_name)
            dialog.destroy()
            
            results = f"=== {col_name} SÜTUN ANALİZİ ===\n\n"
            
            # Eksik değerler
            non_empty = sum(1 for row in self.data if col_idx < len(row) and row[col_idx].strip())
            results += f"Toplam Değer: {len(self.data):,}\n"
            results += f"Dolu Değer: {non_empty:,}\n"
            results += f"Eksik Değer: {len(self.data) - non_empty:,}\n"
            results += f"Doluluk Oranı: {(non_empty/len(self.data)*100):.1f}%\n\n"
            
            if self.column_types.get(col_idx) == 'numeric':
                values = self.get_numeric_values(col_idx)
                if values:
                    results += "SAYISAL İSTATİSTİKLER:\n"
                    results += f"Ortalama: {statistics.mean(values):.2f}\n"
                    results += f"Medyan: {statistics.median(values):.2f}\n"
                    results += f"Min: {min(values):.2f}\n"
                    results += f"Max: {max(values):.2f}\n"
                    if len(values) > 1:
                        results += f"Std Sapma: {statistics.stdev(values):.2f}\n"
                        results += f"Varyans: {statistics.variance(values):.2f}\n"
                    
                    # Çeyrekler
                    sorted_vals = sorted(values)
                    q1 = sorted_vals[len(sorted_vals)//4]
                    q3 = sorted_vals[3*len(sorted_vals)//4]
                    results += f"Q1 (%25): {q1:.2f}\n"
                    results += f"Q3 (%75): {q3:.2f}\n"
                    results += f"IQR: {q3-q1:.2f}\n"
            else:
                # Kategorik sütun
                values = []
                for row in self.data:
                    if col_idx < len(row) and row[col_idx].strip():
                        values.append(row[col_idx])
                
                if values:
                    results += "KATEGORİK ANALİZ:\n"
                    results += f"Benzersiz Değer: {len(set(values)):,}\n\n"
                    
                    # En sık değerler
                    counter = Counter(values)
                    results += "En Sık 10 Değer:\n"
                    for value, count in counter.most_common(10):
                        pct = (count/len(values))*100
                        results += f"  {value[:30]}: {count:,} (%{pct:.1f})\n"
            
            self.results_text.delete("1.0", "end")
            self.results_text.insert("1.0", results)
            self.status_bar.configure(text=f"{col_name} sütunu analiz edildi")
        
        ctk.CTkButton(
            dialog,
            text="Analiz Et",
            command=analyze_column,
            height=35
        ).pack(pady=20)
    
    def show_frequency_analysis(self):
        if not self.data:
            return
            
        self.tabview.set("Analiz Sonuçları")
        
        # Kategorik sütunları bul
        text_columns = [(idx, header) for idx, header in enumerate(self.headers) 
                       if self.column_types.get(idx) == 'text']
        
        if not text_columns:
            messagebox.showinfo("Bilgi", "Frekans analizi için kategorik sütun bulunamadı!")
            return
        
        results = "=== FREKANS ANALİZİ ===\n\n"
        
        for idx, header in text_columns[:5]:  # İlk 5 kategorik sütun
            values = []
            for row in self.data:
                if idx < len(row) and row[idx].strip():
                    values.append(row[idx])
            
            if values:
                results += f"\n{header}:\n"
                counter = Counter(values)
                
                for value, count in counter.most_common(10):
                    pct = (count/len(values))*100
                    bar = "█" * int(pct/2)  # Basit bar grafik
                    results += f"  {value[:25]:30} {count:6,} (%{pct:5.1f}) {bar}\n"
        
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", results)
        self.status_bar.configure(text="Frekans analizi tamamlandı")
    
    def show_histogram(self):
        if not MATPLOTLIB_AVAILABLE or not self.data:
            return
        
        # Sayısal sütunları bul
        numeric_cols = [(idx, header) for idx, header in enumerate(self.headers) 
                       if self.column_types.get(idx) == 'numeric']
        
        if not numeric_cols:
            messagebox.showinfo("Bilgi", "Histogram için sayısal sütun bulunamadı!")
            return
        
        # Sütun seçimi
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Histogram - Sütun Seç")
        dialog.geometry("300x400")
        
        ctk.CTkLabel(dialog, text="Sütun seçin:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        selected_col = ctk.StringVar(value=self.headers[numeric_cols[0][0]])
        
        for idx, header in numeric_cols:
            ctk.CTkRadioButton(
                dialog,
                text=header,
                variable=selected_col,
                value=header
            ).pack(pady=5, padx=20, anchor="w")
        
        def create_histogram():
            col_name = selected_col.get()
            col_idx = self.headers.index(col_name)
            dialog.destroy()
            
            self.tabview.set("Grafik")
            
            # Önceki grafiği temizle
            for widget in self.graph_frame.winfo_children():
                widget.destroy()
            
            values = self.get_numeric_values(col_idx)
            
            # Grafik oluştur
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor('#2b2b2b')
            ax.set_facecolor('#2b2b2b')
            
            ax.hist(values, bins=30, color='#1f77b4', alpha=0.7, edgecolor='white')
            ax.set_title(f'{col_name} - Histogram', color='white', fontsize=14, pad=20)
            ax.set_xlabel(col_name, color='white')
            ax.set_ylabel('Frekans', color='white')
            ax.tick_params(colors='white')
            
            # İstatistik bilgileri
            stats_text = f"Ort: {statistics.mean(values):.2f}\nMed: {statistics.median(values):.2f}"
            ax.text(0.98, 0.95, stats_text, transform=ax.transAxes, 
                   color='white', fontsize=10, verticalalignment='top', 
                   horizontalalignment='right',
                   bbox=dict(boxstyle='round', facecolor='#2b2b2b', alpha=0.8))
            
            plt.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
            self.status_bar.configure(text=f"{col_name} histogramı oluşturuldu")
        
        ctk.CTkButton(
            dialog,
            text="Histogram Oluştur",
            command=create_histogram,
            height=35
        ).pack(pady=20)
    
    def show_bar_chart(self):
        if not MATPLOTLIB_AVAILABLE or not self.data:
            return
        
        # Kategorik sütunları bul
        text_cols = [(idx, header) for idx, header in enumerate(self.headers) 
                    if self.column_types.get(idx) == 'text']
        
        if not text_cols:
            messagebox.showinfo("Bilgi", "Bar grafik için kategorik sütun bulunamadı!")
            return
        
        # Sütun seçimi
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Bar Grafik - Sütun Seç")
        dialog.geometry("300x400")
        
        ctk.CTkLabel(dialog, text="Sütun seçin:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        selected_col = ctk.StringVar(value=self.headers[text_cols[0][0]])
        
        for idx, header in text_cols:
            ctk.CTkRadioButton(
                dialog,
                text=header,
                variable=selected_col,
                value=header
            ).pack(pady=5, padx=20, anchor="w")
        
        def create_bar_chart():
            col_name = selected_col.get()
            col_idx = self.headers.index(col_name)
            dialog.destroy()
            
            self.tabview.set("Grafik")
            
            # Önceki grafiği temizle
            for widget in self.graph_frame.winfo_children():
                widget.destroy()
            
            # Değerleri topla
            values = []
            for row in self.data:
                if col_idx < len(row) and row[col_idx].strip():
                    values.append(row[col_idx])
            
            counter = Counter(values)
            top_items = counter.most_common(10)
            
            labels = [item[0][:20] for item in top_items]
            counts = [item[1] for item in top_items]
            
            # Grafik oluştur
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor('#2b2b2b')
            ax.set_facecolor('#2b2b2b')
            
            bars = ax.bar(range(len(labels)), counts, color='#ff7f0e', alpha=0.7)
            ax.set_title(f'{col_name} - En Sık 10 Değer', color='white', fontsize=14, pad=20)
            ax.set_xlabel('Değerler', color='white')
            ax.set_ylabel('Frekans', color='white')
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=45, ha='right', color='white')
            ax.tick_params(colors='white')
            
            # Değerleri barların üstüne yaz
            for bar, count in zip(bars, counts):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, 
                       str(count), ha='center', va='bottom', color='white')
            
            plt.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
            self.status_bar.configure(text=f"{col_name} bar grafiği oluşturuldu")
        
        ctk.CTkButton(
            dialog,
            text="Bar Grafik Oluştur",
            command=create_bar_chart,
            height=35
        ).pack(pady=20)
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = DataAnalyzer()
    app.run()