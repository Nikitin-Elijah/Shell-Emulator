import os
import sys
import zipfile
import tkinter as tk
from tkinter import scrolledtext, messagebox


class ShellEmulator:
    def __init__(self, username, hostname, zip_path):
        self.username = username
        self.hostname = hostname
        self.current_path = '/'
        self.virtual_fs = {}
        self.load_virtual_fs(zip_path)
        self.init_gui()

    def load_virtual_fs(self, zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                # Создаем структуру виртуальной файловой системы
                self.virtual_fs[self.current_path + member] = zip_ref.read(member)

    def init_gui(self):
        self.window = tk.Tk()
        self.window.title(f"{self.username}@{self.hostname} Shell Emulator")

        self.text_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill='both')
        self.text_area.bind("<Return>", self.process_command)
        self.text_area.insert(tk.END, f"{self.username}@{self.hostname}:{self.current_path}$ ")

        self.window.mainloop()

    def process_command(self, event):
        command = self.text_area.get("end-2c linestart", "end-1c").strip()
        self.text_area.insert(tk.END, '\n')
        self.execute_command(command)
        self.text_area.insert(tk.END, f"{self.username}@{self.hostname}:{self.current_path}$ ")
        self.text_area.see(tk.END)
        return "break"

    def execute_command(self, command):
        cmd_parts = command.split()
        if not cmd_parts:
            return  # Игнорировать пустые команды

        cmd = cmd_parts[1]  # Получение первой части команды

        if cmd == 'exit':
            self.window.quit()
        elif cmd == 'ls':
            self.list_dir()
        elif cmd == 'cd':
            if len(cmd_parts) > 1:
                self.change_dir(cmd_parts[2])
            else:
                messagebox.showerror("Ошибка", "Использование: cd <каталог>")
        elif cmd == 'chown':
            self.change_owner(cmd_parts[2:])
        elif cmd == 'uname':
            self.show_uname()
        else:
            messagebox.showerror("Ошибка", f"Неизвестная команда: {cmd}")

    def list_dir(self):
        # Получение списка файлов в текущем каталоге
        files = [name for name in self.virtual_fs.keys() if name.startswith(self.current_path)]
        if not files:
            self.text_area.insert(tk.END, "Файлы не найдены.\n")
        else:
            # Фильтруем файлы, чтобы показать только те, которые находятся в текущем каталоге
            current_dir_files = [name.split(self.current_path)[1] for name in files
                                 if name.count('/') == self.current_path.count('/')
                                 or name.count('/') == self.current_path.count('/') + 1 and name[-1] == '/']
            if not current_dir_files:
                self.text_area.insert(tk.END, "Файлы не найдены.\n")
            else:
                self.text_area.insert(tk.END, "\n".join(os.path.basename(file) for file in current_dir_files if file != '') + '\n')

    def change_dir(self, path):
        if path == '..':
            # Переход на уровень выше
            if self.current_path != '/':
                self.current_path = '/'.join(self.current_path.split('/')[:-2]) or '/'
        else:
            new_path = os.path.join(self.current_path, path)
            # Проверяем, что новый путь существует в виртуальной файловой системе
            if any(name.startswith(new_path + '/') for name in self.virtual_fs.keys()) or new_path in self.virtual_fs:
                self.current_path = new_path + '/'
            else:
                messagebox.showerror("Ошибка", "Нет такого файла или каталога")

    def change_owner(self, args):
        print(args)
        if len(args) == 2:
            self.text_area.insert(tk.END, f"Изменен владелец {args[0]} на {args[1]}\n")
        else:
            messagebox.showerror("Ошибка", "Использование: chown <файл> <новый_владелец>")

    def show_uname(self):
        uname_info = f"Система: {self.hostname}, Пользователь: {self.username}"
        self.text_area.insert(tk.END, uname_info + '\n')


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Использование: python shell_emulator.py <имя_пользователя> <имя_хоста> <путь_к_zip>")
        sys.exit(1)

    username = sys.argv[1]
    hostname = sys.argv[2]
    zip_path = sys.argv[3]

    # Проверка существования файла
    if not os.path.isfile(zip_path):
        print(f"Ошибка: Файл {zip_path} не существует.")
        sys.exit(1)

    ShellEmulator(username, hostname, zip_path)
