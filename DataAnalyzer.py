import customtkinter as ctk
from tkinter import filedialog, messagebox
import csv
import os
from collections import Counter
import statistics

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

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
        
        self.data = []  
        self.headers = []  
        self.file_path = None
        self.column_types = {}  
        
        self.setup_ui()
        
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showwarning("Uyari", 
                "Matplotlib kutuphanesi bulunamadi!\n\n"
                "Grafik ozellikleri devre disi.\n"
                "Kurmak icin: pip install matplotlib")
        
    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.left_panel = ctk.CTkFrame(self.main_frame, width=300)
        self.left_panel.pack(side="left", fill="y", padx=(0, 10))
        self.left_panel.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            self.left_panel, 
            text="DataAnalyzer", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        subtitle = ctk.CTkLabel(
            self.left_panel,
            text="CSV Veri Analiz Araci",
            font=ctk.CTkFont(size=12)
        )
        subtitle.pack(pady=(0, 10))
        
        self.load_btn = ctk.CTkButton(
            self.left_panel,
            text="CSV Dosyasi Yuke",
            command=self.load_file,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.load_btn.pack(pady=10, padx=20, fill="x")
        
        self.file_info = ctk.CTkLabel(
            self.left_panel,
            text="Henuz dosya yuklenmedi",
            font=ctk.CTkFont(size=12),
            wraplength=250
        )
        self.file_info.pack(pady=5)
        
        ctk.CTkFrame(self.left_panel, height=2).pack(fill="x", pady=15, padx=20)
        
        options_label = ctk.CTkLabel(
            self.left_panel,
            text="Analiz Secenekleri",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        options_label.pack(pady=10)
        
        self.stats_btn = ctk.CTkButton(
            self.left_panel,
            text="Temel Istatistikler",
            command=self.show_statistics,
            state="disabled",
            height=35
        )
        self.stats_btn.pack(pady=5, padx=20, fill="x")
        
        self.column_btn = ctk.CTkButton(
            self.left_panel,
            text="Sutun Analizi",
            command=self.show_column_analysis,
            state="disabled",
            height=35
        )
        self.column_btn.pack(pady=5, padx=20, fill="x")
        
        self.freq_btn = ctk.CTkButton(
            self.left_panel,
            text="Frekans Analizi",
            command=self.show_frequency_analysis,
            state="disabled",
            height=35
        )
        self.freq_btn.pack(pady=5, padx=20, fill="x")
        
        if MATPLOTLIB_AVAILABLE:
            self.hist_btn = ctk.CTkButton(
                self.left_panel,
                text="Histogram",
                command=self.show_histogram,
                state="disabled",
                height=35
            )
            self.hist_btn.pack(pady=5, padx=20, fill="x")
            
            self.bar_btn = ctk.CTkButton(
                self.left_panel,
                text="Bar Grafik",
                command=self.show_bar_chart,
                state="disabled",
                height=35
            )
            self.bar_btn.pack(pady=5, padx=20, fill="x")
        else:
            self.hist_btn = ctk.CTkButton(
                self.left_panel,
                text="Histogram (Matplotlib yok)",
                state="disabled",
                height=35
            )
            self.hist_btn.pack(pady=5, padx=20, fill="x")
            
            self.bar_btn = ctk.CTkButton(
                self.left_panel,
                text="Bar Grafik (Matplotlib yok)",
                state="disabled",
                height=35
            )
            self.bar_btn.pack(pady=5, padx=20, fill="x")
        
        ctk.CTkFrame(self.left_panel, height=2).pack(fill="x", pady=15, padx=20)
        
        preview_label = ctk.CTkLabel(
            self.left_panel,
            text="Onizleme Satir Sayisi",
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
        
        self.right_panel = ctk.CTkFrame(self.main_frame)
        self.right_panel.pack(side="right", fill="both", expand=True)
        
        self.tabview = ctk.CTkTabview(self.right_panel)
        self.tabview.pack(fill="both", expand=True)
        
        self.tabview.add("Veri Onizleme")
        self.tabview.add("Analiz Sonuclari")
        if MATPLOTLIB_AVAILABLE:
            self.tabview.add("Grafik")
        
        self.preview_text = ctk.CTkTextbox(
            self.tabview.tab("Veri Onizleme"),
            font=ctk.CTkFont(family="Courier", size=11)
        )
        self.preview_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.results_text = ctk.CTkTextbox(
            self.tabview.tab("Analiz Sonuclari"),
            font=ctk.CTkFont(family="Courier", size=11)
        )
        self.results_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        if MATPLOTLIB_AVAILABLE:
            self.graph_frame = ctk.CTkFrame(self.tabview.tab("Grafik"))
            self.graph_frame.pack(fill="both", expand=True)

        self.status_bar = ctk.CTkLabel(
            self.window,
            text="Hazir - CSV dosyasi yukleyin",
            anchor="w",
            font=ctk.CTkFont(size=11)
        )
        self.status_bar.pack(side="bottom", fill="x", padx=10, pady=5)
    
    def detect_delimiter(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            
        delimiters = [',', ';', '\t', '|']
        counts = {d: first_line.count(d) for d in delimiters}
        best_delimiter = max(counts, key=counts.get)
        
        if counts[best_delimiter] == 0:
            return ','
        return best_delimiter
    
    def detect_column_types(self):
        self.column_types = {}
        
        for col_idx, header in enumerate(self.headers):
            is_numeric = True
            numeric_count = 0
            total_count = 0
            
            for row in self.data[:min(100, len(self.data))]:
                if col_idx < len(row) and row[col_idx].strip():
                    total_count += 1
                    try:
                        float(row[col_idx].replace(',', '.'))
                        numeric_count += 1
                    except:
                        pass
            
            if total_count > 0 and (numeric_count / total_count) > 0.9:
                self.column_types[col_idx] = 'numeric'
            else:
                self.column_types[col_idx] = 'text'
    
    def get_numeric_values(self, col_idx):
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
            title="CSV dosyasi secin",
            filetypes=[
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.status_bar.configure(text=f"Yukleniyor: {os.path.basename(file_path)}")
                self.window.update()
                
                delimiter = self.detect_delimiter(file_path)
                
                self.data = []
                self.headers = []
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter=delimiter)
                    
                    try:
                        self.headers = next(reader)
                    except StopIteration:
                        messagebox.showerror("Hata", "Dosya bos!")
                        return
                    
                    for row in reader:
                        self.data.append(row)
                
                self.file_path = file_path
                
                self.detect_column_types()
                
                self.stats_btn.configure(state="normal")
                self.column_btn.configure(state="normal")
                self.freq_btn.configure(state="normal")
                
                if MATPLOTLIB_AVAILABLE:
                    if any(t == 'numeric' for t in self.column_types.values()):
                        self.hist_btn.configure(state="normal")
                    
                    if any(t == 'text' for t in self.column_types.values()):
                        self.bar_btn.configure(state="normal")
                
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path) / 1024
                
                info_text = f"Dosya: {file_name}\n"
                info_text += f"Satir: {len(self.data):,}\n"
                info_text += f"Sutun: {len(self.headers)}\n"
                info_text += f"Boyut: {file_size:.1f} KB\n"
                info_text += f"Ayrac: '{delimiter}'\n"
                info_text += f"Sayisal Sutun: {sum(1 for t in self.column_types.values() if t == 'numeric')}"
                
                self.file_info.configure(text=info_text)
                
                self.update_preview()
                
                self.status_bar.configure(text=f"Yuklendi: {file_name} ({len(self.data):,} satir)")
                
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya yuklenirken hata olustu:\n{str(e)}")
                self.status_bar.configure(text="Hata olustu")
    
    def update_preview(self, choice=None):
        if self.data:
            try:
                n_rows = min(int(self.preview_rows.get()), len(self.data))
                
                preview_text = f"=== VERI ONIZLEME (Ilk {n_rows} satir) ===\n\n"
                
                preview_text += " | ".join(self.headers) + "\n"
                preview_text += "-" * 100 + "\n"
                
                for i in range(n_rows):
                    row = self.data[i]
                    preview_text += " | ".join(str(cell) for cell in row) + "\n"
                
                preview_text += f"\n=== SUTUN BILGILERI ===\n\n"
                
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
                messagebox.showerror("Hata", f"Onizleme hatasi: {str(e)}")
    
    def show_statistics(self):
        if not self.data:
            return
            
        self.tabview.set("Analiz Sonuclari")
        
        results = "=== TEMEL ISTATISTIKLER ===\n\n"
        
        results += f"Toplam Satir: {len(self.data):,}\n"
        results += f"Toplam Sutun: {len(self.headers)}\n\n"
        
        for idx, header in enumerate(self.headers):
            if self.column_types.get(idx) == 'numeric':
                values = self.get_numeric_values(idx)
                
                if values:
                    results += f"\n{header}:\n"
                    results += f"  - Deger Sayisi: {len(values):,}\n"
                    results += f"  - Eksik Deger: {len(self.data) - len(values):,}\n"
                    results += f"  - Ortalama: {statistics.mean(values):.2f}\n"
                    results += f"  - Medyan: {statistics.median(values):.2f}\n"
                    results += f"  - Min: {min(values):.2f}\n"
                    results += f"  - Max: {max(values):.2f}\n"
                    
                    if len(values) > 1:
                        results += f"  - Std Sapma: {statistics.stdev(values):.2f}\n"
        
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", results)
        self.status_bar.configure(text="Istatistikler hesaplandi")
    
    def show_column_analysis(self):
        if not self.data:
            return
            
        self.tabview.set("Analiz Sonuclari")
        
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Sutun Sec")
        dialog.geometry("300x400")
        
        ctk.CTkLabel(dialog, text="Analiz edilecek sutunu secin:", 
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
            
            results = f"=== {col_name} SUTUN ANALIZI ===\n\n"
            
            non_empty = sum(1 for row in self.data if col_idx < len(row) and row[col_idx].strip())
            results += f"Toplam Deger: {len(self.data):,}\n"
            results += f"Dolu Deger: {non_empty:,}\n"
            results += f"Eksik Deger: {len(self.data) - non_empty:,}\n"
            results += f"Doluluk Orani: {(non_empty/len(self.data)*100):.1f}%\n\n"
            
            if self.column_types.get(col_idx) == 'numeric':
                values = self.get_numeric_values(col_idx)
                if values:
                    results += "SAYISAL ISTATISTIKLER:\n"
                    results += f"Ortalama: {statistics.mean(values):.2f}\n"
                    results += f"Medyan: {statistics.median(values):.2f}\n"
                    results += f"Min: {min(values):.2f}\n"
                    results += f"Max: {max(values):.2f}\n"
                    if len(values) > 1:
                        results += f"Std Sapma: {statistics.stdev(values):.2f}\n"
                        results += f"Varyans: {statistics.variance(values):.2f}\n"
                    
                    sorted_vals = sorted(values)
                    q1 = sorted_vals[len(sorted_vals)//4]
                    q3 = sorted_vals[3*len(sorted_vals)//4]
                    results += f"Q1 (%25): {q1:.2f}\n"
                    results += f"Q3 (%75): {q3:.2f}\n"
                    results += f"IQR: {q3-q1:.2f}\n"
            else:
                values = []
                for row in self.data:
                    if col_idx < len(row) and row[col_idx].strip():
                        values.append(row[col_idx])
                
                if values:
                    results += "KATEGORIK ANALIZ:\n"
                    results += f"Benzersiz Deger: {len(set(values)):,}\n\n"
                    
                    counter = Counter(values)
                    results += "En Sik 10 Deger:\n"
                    for value, count in counter.most_common(10):
                        pct = (count/len(values))*100
                        results += f"  {value[:30]}: {count:,} (%{pct:.1f})\n"
            
            self.results_text.delete("1.0", "end")
            self.results_text.insert("1.0", results)
            self.status_bar.configure(text=f"{col_name} sutunu analiz edildi")
        
        ctk.CTkButton(
            dialog,
            text="Analiz Et",
            command=analyze_column,
            height=35
        ).pack(pady=20)
    
    def show_frequency_analysis(self):
        if not self.data:
            return
            
        self.tabview.set("Analiz Sonuclari")
        
        text_columns = [(idx, header) for idx, header in enumerate(self.headers) 
                       if self.column_types.get(idx) == 'text']
        
        if not text_columns:
            messagebox.showinfo("Bilgi", "Frekans analizi icin kategorik sutun bulunamadi!")
            return
        
        results = "=== FREKANS ANALIZI ===\n\n"
        
        for idx, header in text_columns[:5]:
            values = []
            for row in self.data:
                if idx < len(row) and row[idx].strip():
                    values.append(row[idx])
            
            if values:
                results += f"\n{header}:\n"
                counter = Counter(values)
                
                for value, count in counter.most_common(10):
                    pct = (count/len(values))*100
                    bar = "#" * int(pct/2)
                    results += f"  {value[:25]:30} {count:6,} (%{pct:5.1f}) {bar}\n"
        
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", results)
        self.status_bar.configure(text="Frekans analizi tamamlandi")
    
    def show_histogram(self):
        if not MATPLOTLIB_AVAILABLE or not self.data:
            return
        
        numeric_cols = [(idx, header) for idx, header in enumerate(self.headers) 
                       if self.column_types.get(idx) == 'numeric']
        
        if not numeric_cols:
            messagebox.showinfo("Bilgi", "Histogram icin sayisal sutun bulunamadi!")
            return
        
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Histogram - Sutun Sec")
        dialog.geometry("300x400")
        
        ctk.CTkLabel(dialog, text="Sutun secin:", 
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
            
            for widget in self.graph_frame.winfo_children():
                widget.destroy()
            
            values = self.get_numeric_values(col_idx)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor('#2b2b2b')
            ax.set_facecolor('#2b2b2b')
            
            ax.hist(values, bins=30, color='#1f77b4', alpha=0.7, edgecolor='white')
            ax.set_title(f'{col_name} - Histogram', color='white', fontsize=14, pad=20)
            ax.set_xlabel(col_name, color='white')
            ax.set_ylabel('Frekans', color='white')
            ax.tick_params(colors='white')
            
            stats_text = f"Ort: {statistics.mean(values):.2f}\nMed: {statistics.median(values):.2f}"
            ax.text(0.98, 0.95, stats_text, transform=ax.transAxes, 
                   color='white', fontsize=10, verticalalignment='top', 
                   horizontalalignment='right',
                   bbox=dict(boxstyle='round', facecolor='#2b2b2b', alpha=0.8))
            
            plt.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
            self.status_bar.configure(text=f"{col_name} histogrami olusturuldu")
        
        ctk.CTkButton(
            dialog,
            text="Histogram Olustur",
            command=create_histogram,
            height=35
        ).pack(pady=20)
    
    def show_bar_chart(self):
        if not MATPLOTLIB_AVAILABLE or not self.data:
            return
        
        text_cols = [(idx, header) for idx, header in enumerate(self.headers) 
                    if self.column_types.get(idx) == 'text']
        
        if not text_cols:
            messagebox.showinfo("Bilgi", "Bar grafik icin kategorik sutun bulunamadi!")
            return
        
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Bar Grafik - Sutun Sec")
        dialog.geometry("300x400")
        
        ctk.CTkLabel(dialog, text="Sutun secin:", 
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
            
            for widget in self.graph_frame.winfo_children():
                widget.destroy()
            
            values = []
            for row in self.data:
                if col_idx < len(row) and row[col_idx].strip():
                    values.append(row[col_idx])
            
            counter = Counter(values)
            top_items = counter.most_common(10)
            
            labels = [item[0][:20] for item in top_items]
            counts = [item[1] for item in top_items]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor('#2b2b2b')
            ax.set_facecolor('#2b2b2b')
            
            bars = ax.bar(range(len(labels)), counts, color='#ff7f0e', alpha=0.7)
            ax.set_title(f'{col_name} - En Sik 10 Deger', color='white', fontsize=14, pad=20)
            ax.set_xlabel('Degerler', color='white')
            ax.set_ylabel('Frekans', color='white')
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=45, ha='right', color='white')
            ax.tick_params(colors='white')
            
            for bar, count in zip(bars, counts):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, 
                       str(count), ha='center', va='bottom', color='white')
            
            plt.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
            self.status_bar.configure(text=f"{col_name} bar grafigi olusturuldu")
        
        ctk.CTkButton(
            dialog,
            text="Bar Grafik Olustur",
            command=create_bar_chart,
            height=35
        ).pack(pady=20)
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = DataAnalyzer()
    app.run()
