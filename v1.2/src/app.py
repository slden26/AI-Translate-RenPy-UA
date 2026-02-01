import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import configparser
import re
import time
from openai import OpenAI

# Глобальные константы
_CONFIG_INI = "settings.ini"

class TranslationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Translate RenPy UA v1.2")
        self.root.resizable(False, False)
        
        # Переменные интерфейса
        self.api_key_var = tk.StringVar()
        self.api_url_var = tk.StringVar(value="https://openrouter.ai/api/v1")
        self.translate_to_var = tk.StringVar(value="Russian")
        self.input_path_var = tk.StringVar()
        self.output_path_var = tk.StringVar()
        self.engine_var = tk.StringVar(value="google/gemini-2.0-flash-lite:free")
        self.batch_size_var = tk.StringVar(value="10")
        self.temperature_var = tk.StringVar(value="0.3")
        self.prompt_var = tk.StringVar(value="Professional Ren'Py translator. Translate to Russian. Preserve tags like [] and {}. Format: 'index:translation'. No comments.")
        
        self.is_running = False
        self.saved_glossary = ""
        self.load_config()
        self.create_widgets()

    def create_widgets(self):
        padding = {'padx': 5, 'pady': 5}
        
        # Основной контейнер
        main_container = tk.Frame(self.root)
        main_container.pack(padx=10, pady=10)

        # ЛЕВАЯ ПАНЕЛЬ
        left_panel = tk.Frame(main_container)
        left_panel.grid(row=0, column=0, sticky='n')

        tk.Label(left_panel, text="API Key:").grid(row=0, column=0, sticky='e', **padding)
        tk.Entry(left_panel, textvariable=self.api_key_var, width=45, show="*").grid(row=0, column=1, sticky='w', **padding)
        
        tk.Label(left_panel, text="API URL:").grid(row=1, column=0, sticky='e', **padding)
        tk.Entry(left_panel, textvariable=self.api_url_var, width=45).grid(row=1, column=1, sticky='w', **padding)

        tk.Label(left_panel, text="Target Lang:").grid(row=2, column=0, sticky='e', **padding)
        tk.Entry(left_panel, textvariable=self.translate_to_var, width=45).grid(row=2, column=1, sticky='w', **padding)

        tk.Label(left_panel, text="Input Path:").grid(row=3, column=0, sticky='e', **padding)
        in_frame = tk.Frame(left_panel)
        in_frame.grid(row=3, column=1, sticky='w')
        tk.Entry(in_frame, textvariable=self.input_path_var, width=35).pack(side=tk.LEFT)
        tk.Button(in_frame, text="...", command=self.browse_input).pack(side=tk.LEFT, padx=2)

        tk.Label(left_panel, text="Output Path:").grid(row=4, column=0, sticky='e', **padding)
        out_frame = tk.Frame(left_panel)
        out_frame.grid(row=4, column=1, sticky='w')
        tk.Entry(out_frame, textvariable=self.output_path_var, width=35).pack(side=tk.LEFT)
        tk.Button(out_frame, text="...", command=self.browse_output).pack(side=tk.LEFT, padx=2)

        tk.Label(left_panel, text="Model Engine:").grid(row=5, column=0, sticky='e', **padding)
        tk.Entry(left_panel, textvariable=self.engine_var, width=45).grid(row=5, column=1, sticky='w', **padding)

        tk.Label(left_panel, text="Batch / Temp:").grid(row=6, column=0, sticky='e', **padding)
        p_frame = tk.Frame(left_panel)
        p_frame.grid(row=6, column=1, sticky='w')
        tk.Entry(p_frame, textvariable=self.batch_size_var, width=10).pack(side=tk.LEFT)
        tk.Label(p_frame, text=" Temp:").pack(side=tk.LEFT)
        tk.Entry(p_frame, textvariable=self.temperature_var, width=10).pack(side=tk.LEFT)

        # ПРАВАЯ ПАНЕЛЬ (Глоссарий)
        right_panel = tk.Frame(main_container)
        right_panel.grid(row=0, column=1, rowspan=7, padx=(20, 0), sticky='n')
        
        tk.Label(right_panel, text="Glossary (Name=Translation):", font=('Arial', 9, 'bold')).pack()
        self.glossary_text = scrolledtext.ScrolledText(right_panel, width=35, height=15, font=('Consolas', 9))
        self.glossary_text.pack()
        if self.saved_glossary:
            self.glossary_text.insert(tk.END, self.saved_glossary)

        # НИЖНЯЯ ПАНЕЛЬ
        bottom_panel = tk.Frame(self.root)
        bottom_panel.pack(fill='x', padx=15, pady=(0, 10))

        tk.Label(bottom_panel, text="System Prompt:").pack(anchor='w')
        tk.Entry(bottom_panel, textvariable=self.prompt_var, width=100).pack(fill='x', pady=2)

        btn_row = tk.Frame(bottom_panel)
        btn_row.pack(fill='x', pady=5)
        
        self.start_button = tk.Button(btn_row, text="START PROCESS", command=self.start_translation, bg="#2ecc71", fg="white", font=('Arial', 10, 'bold'), width=20)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(btn_row, text="STOP", command=self.stop_translation, state=tk.DISABLED, bg="#e74c3c", fg="white", width=15)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.progress_bar = ttk.Progressbar(bottom_panel, orient='horizontal', mode='determinate')
        self.progress_bar.pack(fill='x', pady=5)

        self.log_text = tk.Text(bottom_panel, height=10, width=100, font=('Consolas', 9))
        self.log_text.pack()

    def browse_input(self):
        path = filedialog.askdirectory()
        if path: self.input_path_var.set(path)

    def browse_output(self):
        path = filedialog.askdirectory()
        if path: self.output_path_var.set(path)

    def log(self, message):
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)

    def save_config(self):
        config = configparser.ConfigParser()
        config['Settings'] = {
            "api_key": self.api_key_var.get(),
            "api_url": self.api_url_var.get(),
            "engine": self.engine_var.get(),
            "batch_size": self.batch_size_var.get(),
            "temperature": self.temperature_var.get(),
            "prompt": self.prompt_var.get(),
            "translate_to": self.translate_to_var.get(),
            "input_path": self.input_path_var.get(),
            "output_path": self.output_path_var.get(),
            "glossary": self.glossary_text.get(1.0, tk.END).strip()
        }
        with open(_CONFIG_INI, "w", encoding='utf-8') as f:
            config.write(f)

    def load_config(self):
        config = configparser.ConfigParser()
        if os.path.exists(_CONFIG_INI):
            config.read(_CONFIG_INI, encoding='utf-8')
            if 'Settings' in config:
                s = config['Settings']
                self.api_key_var.set(s.get("api_key", ""))
                self.api_url_var.set(s.get("api_url", "https://openrouter.ai/api/v1"))
                self.engine_var.set(s.get("engine", "google/gemini-2.0-flash-lite:free"))
                self.batch_size_var.set(s.get("batch_size", "10"))
                self.temperature_var.set(s.get("temperature", "0.3"))
                self.prompt_var.set(s.get("prompt", self.prompt_var.get()))
                self.translate_to_var.set(s.get("translate_to", "Russian"))
                self.input_path_var.set(s.get("input_path", ""))
                self.output_path_var.set(s.get("output_path", ""))
                self.saved_glossary = s.get("glossary", "")

    def start_translation(self):
        if not self.api_key_var.get():
            messagebox.showwarning("Warning", "Enter API Key!")
            return
        self.save_config()
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        threading.Thread(target=self.process_files, daemon=True).start()

    def stop_translation(self):
        self.is_running = False
        self.log("Stopping process...")

    def process_files(self):
        input_dir = self.input_path_var.get()
        output_dir = self.output_path_var.get()
        if not input_dir or not output_dir:
            self.log("Error: Paths not selected!")
            self.reset_ui(); return

        files_to_process = []
        for root, _, filenames in os.walk(input_dir):
            for file in filenames:
                if file.endswith('.rpy'):
                    rel_path = os.path.relpath(os.path.join(root, file), input_dir)
                    files_to_process.append(rel_path)

        if not files_to_process:
            self.log("No .rpy files found!"); self.reset_ui(); return

        self.progress_bar['maximum'] = len(files_to_process)
        url = self.api_url_var.get().strip()
        if "127.0.0.1" in url and not url.endswith("/v1"):
            url = f"{url.rstrip('/')}/v1"
            
        client = OpenAI(api_key=self.api_key_var.get(), base_url=url)

        for idx, rel_path in enumerate(files_to_process):
            if not self.is_running: break
            in_f, out_f = os.path.join(input_dir, rel_path), os.path.join(output_dir, rel_path)
            os.makedirs(os.path.dirname(out_f), exist_ok=True)
            self.log(f"File {idx+1}/{len(files_to_process)}: {rel_path}")
            self.translate_file(in_f, out_f, client)
            self.progress_bar['value'] = idx + 1
        
        self.log("All tasks completed!"); self.reset_ui()

    def translate_file(self, in_path, out_path, client):
        with open(in_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        items = []
        pattern = re.compile(r'^(?P<prefix>\s*(?:old\s+|new\s+|".*?"\s+|[\w\d_]+\s+)?")(?P<text>.+?)(?P<suffix>")(?P<extra>.*)$')
        for i, line in enumerate(lines):
            match = pattern.match(line)
            if match and not line.strip().startswith(('#', 'default', 'define')):
                items.append({'index': i, 'text': match.group('text'), 'match': match})

        batch_size = int(self.batch_size_var.get())
        for i in range(0, len(items), batch_size):
            if not self.is_running: break
            batch = items[i:i + batch_size]
            try:
                processed = self.call_ai([it['text'] for it in batch], client)
                for j, new_text in enumerate(processed):
                    if j < len(batch):
                        it = batch[j]; m = it['match']
                        lines[it['index']] = f"{m.group('prefix')}{new_text}{m.group('suffix')}{m.group('extra')}\n"
            except Exception as e:
                self.log(f"AI Error: {str(e)}")

        with open(out_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

    def call_ai(self, texts, client):
        glossary = self.glossary_text.get(1.0, tk.END).strip()
        sys_prompt = self.prompt_var.get()
        if glossary:
            sys_prompt += f"\n\nSTRICT GLOSSARY (Translate names exactly as shown):\n{glossary}"
        
        user_content = f"TARGET: {self.translate_to_var.get()}\n\nTEXTS:\n" + "\n".join([f"{i}:{t}" for i, t in enumerate(texts)])
        
        response = client.chat.completions.create(
            model=self.engine_var.get(),
            messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_content}],
            temperature=float(self.temperature_var.get()),
            stream=False
        )
        
        result_text = response.choices[0].message.content
        results = [None] * len(texts)
        for line in result_text.strip().split('\n'):
            match = re.search(r'(\d+)[:\s.](.*)', line)
            if match:
                idx = int(match.group(1))
                content = match.group(2).strip().strip('"').replace('```renpy', '').replace('```', '').strip()
                if 0 <= idx < len(texts): results[idx] = content
        return [res if res is not None else texts[k] for k, res in enumerate(results)]

    def reset_ui(self):
        self.start_button.config(state=tk.NORMAL); self.stop_button.config(state=tk.DISABLED); self.is_running = False

if __name__ == "__main__":
    root = tk.Tk(); app = TranslationGUI(root); root.mainloop()