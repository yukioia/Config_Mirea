import argparse
import zipfile
import os
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime
import csv

# Функция загрузки виртуальной файловой системы из zip-архива
def load_vfs(zip_path):
    vfs = {}
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            path = file_info.filename.strip('/').split('/')
            current_level = vfs
            for part in path:
                if part not in current_level:
                    if part == path[-1] and not file_info.is_dir():
                        current_level[part] = None  # Файл обозначаем как None
                    else:
                        current_level[part] = {}
                current_level = current_level[part] if isinstance(current_level[part], dict) else current_level
    return vfs

# Класс GUI эмулятора оболочки
class ShellEmulatorGUI:
    def __init__(self, root, vfs, log_path, vfs_path):
        self.root = root
        self.vfs = vfs
        self.log_path = log_path
        self.vfs_path = vfs_path
        self.current_path = ['/']
        self.cwd = self.vfs
        self.modified_files = {}

        self.root.title("Эмулятор оболочки ОС")

        # Область вывода (Console Output Area)
        self.output_area = scrolledtext.ScrolledText(root, width=80, height=20)
        self.output_area.pack()
        self.output_area.configure(state='disabled')  # Делаем виджет только для чтения

        # Поле ввода (Input Field)
        self.input_field = tk.Entry(root, width=80)
        self.input_field.pack()
        self.input_field.bind('<Return>', self.on_enter)
        self.input_field.focus()

        self.display_prompt()

    # Отображение приглашения (prompt)
    def display_prompt(self):
        path_str = os.path.join(*self.current_path)
        self.output_area.configure(state='normal')
        self.output_area.insert(tk.END, f"{path_str}$ ")
        self.output_area.configure(state='disabled')
        self.output_area.see(tk.END)

    # Обработка ввода пользователя после нажатия Enter
    def on_enter(self, event):
        command = self.input_field.get()
        self.output_area.configure(state='normal')
        self.output_area.insert(tk.END, command + '\n')
        self.output_area.configure(state='disabled')
        self.process_command(command)
        self.input_field.delete(0, tk.END)
        if command.strip() != 'exit':
            self.display_prompt()

    # Обработка введенной команды
    def process_command(self, command):
        # Разделяем команду по символу '>' для обработки перенаправления
        if '>' in command:
            command_part, filename = command.split('>', 1)
            command_part = command_part.strip()
            filename = filename.strip()
            redirect = True
        else:
            command_part = command
            filename = None
            redirect = False

        tokens = command_part.strip().split()
        if not tokens:
            return
        cmd, *args = tokens

        if cmd == 'ls':
            output = self.handle_ls(args)
        elif cmd == 'cd':
            self.handle_cd(args)
            output = None
        elif cmd == 'cat':
            output = self.handle_cat(args)
        elif cmd == 'echo':
            output = self.handle_echo(args)
        elif cmd == 'exit':
            self.handle_exit()
            output = None
        else:
            output = f"Команда не найдена: {cmd}\n"

        if redirect and output is not None:
            self.write_to_file(filename, output)
        elif output is not None:
            self.display_output(output)

        self.log_action(command)

    # Метод для вывода текста на экран
    def display_output(self, output):
        self.output_area.configure(state='normal')
        self.output_area.insert(tk.END, output)
        self.output_area.configure(state='disabled')

    # Реализация команды ls
    def handle_ls(self, args):
        if self.cwd:
            entries = self.cwd.keys()
            output = '  '.join(entries) + '\n'
        else:
            output = '\n'
        return output

    # Реализация команды cd
    def handle_cd(self, args):
        if len(args) != 1:
            self.display_output("cd: требуется один аргумент\n")
            return
        path = args[0]
        if path == '/':
            self.current_path = ['/']
            self.update_cwd()
            return
        elif path == '..':
            if len(self.current_path) > 1:
                self.current_path.pop()
            self.update_cwd()
            return
        else:
            path_parts = path.strip('/').split('/')
            temp_path = self.current_path.copy()
            temp_cwd = self.cwd
            for part in path_parts:
                if part in temp_cwd and isinstance(temp_cwd[part], dict):
                    temp_cwd = temp_cwd[part]
                    temp_path.append(part)
                else:
                    self.display_output(f"cd: нет такого файла или каталога: {path}\n")
                    return
            self.current_path = temp_path
            self.cwd = temp_cwd

    # Реализация команды cat
    def handle_cat(self, args):
        if len(args) != 1:
            return "cat: требуется один аргумент\n"
        path = args[0]
        full_path = os.path.join(*self.current_path, path).lstrip('/')
        try:
            # Проверяем, есть ли файл в измененных данных
            if full_path in self.modified_files:
                content = self.modified_files[full_path]
            else:
                with zipfile.ZipFile(self.vfs_path, 'r') as zip_ref:
                    with zip_ref.open(full_path, 'r') as file:
                        content = file.read().decode('utf-8')
            return content + '\n'
        except KeyError:
            return f"cat: нет такого файла или каталога: {path}\n"
        except UnicodeDecodeError:
            return f"cat: невозможно прочитать файл: {path} (не текстовый файл)\n"

    # Реализация команды echo
    def handle_echo(self, args):
        text = ' '.join(args)
        return text + '\n'

    # Метод записи в файл
    def write_to_file(self, filename, content):
        full_path = os.path.join(*self.current_path, filename).lstrip('/')
        # Сохраняем содержимое в словаре modified_files
        self.modified_files[full_path] = content
        # Обновляем структуру ВФС
        self.update_vfs_structure(full_path)

    # Метод обновления структуры ВФС при создании нового файла
    def update_vfs_structure(self, full_path):
        path_parts = full_path.split('/')
        current_level = self.vfs
        for part in path_parts[:-1]:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]
        # Добавляем файл в текущую директорию
        current_level[path_parts[-1]] = None

    # Реализация команды exit
    def handle_exit(self):
        if self.modified_files:
            # Спрашиваем пользователя, хочет ли он сохранить изменения
            save_changes = messagebox.askyesno("Сохранение изменений", "Вы хотите сохранить изменения в виртуальной файловой системе?")
            if save_changes:
                self.save_changes_to_vfs()
        self.root.quit()

    # Сохранение изменений в новый zip-архив
    def save_changes_to_vfs(self):
        # Копируем оригинальный zip-архив в новый
        new_zip_path = self.vfs_path.replace('.zip', '_modified.zip')
        with zipfile.ZipFile(self.vfs_path, 'r') as zip_read:
            with zipfile.ZipFile(new_zip_path, 'w') as zip_write:
                # Список файлов, которые уже были обработаны
                processed_files = set()

                # Обрабатываем исходные файлы
                for item in zip_read.infolist():
                    if item.filename in self.modified_files:
                        zip_write.writestr(item.filename, self.modified_files[item.filename])
                        processed_files.add(item.filename)
                    else:
                        buffer = zip_read.read(item.filename)
                        zip_write.writestr(item, buffer)
                        processed_files.add(item.filename)

                # Добавляем новые файлы
                for filepath, content in self.modified_files.items():
                    if filepath not in processed_files:
                        zip_write.writestr(filepath, content)
        messagebox.showinfo("Сохранение изменений", f"Изменения сохранены в {new_zip_path}")

    # Обновление текущей директории (cwd) после изменений в current_path
    def update_cwd(self):
        self.cwd = self.vfs
        for part in self.current_path[1:]:
            if part in self.cwd:
                self.cwd = self.cwd[part]
            else:
                self.cwd = {}
                break

    # Логирование действия пользователя
    def log_action(self, action):
        with open(self.log_path, 'a', newline='', encoding='utf-8') as csvfile:
            log_writer = csv.writer(csvfile)
            log_writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), action])

# Главный блок запуска программы
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Эмулятор оболочки ОС.')
    parser.add_argument('--vfs_path', type=str, required=True, help='Путь к архиву виртуальной файловой системы')
    parser.add_argument('--log_path', type=str, required=True, help='Путь к лог-файлу')
    args = parser.parse_args()
    vfs_path = args.vfs_path
    log_path = args.log_path

    vfs = load_vfs(vfs_path)

    root = tk.Tk()
    app = ShellEmulatorGUI(root, vfs, log_path, vfs_path)
    root.mainloop()
