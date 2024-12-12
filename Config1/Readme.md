# Создаём файловую систему:
```
mkdir -p vfs/home/user/documents
mkdir -p vfs/home/user/pictures
mkdir -p vfs/etc
mkdir -p vfs/var/log
echo 'Это содержимое файла file1.txt в папке documents.' > vfs/home/user/documents/file1.txt
echo 'Это содержимое файла file2.txt в папке documents.' > vfs/home/user/documents/file2.txt
echo 'Некоторые заметки пользователя.' > vfs/home/user/notes.txt
echo 'Содержимое файла конфигурации.' > vfs/etc/config.cfg
echo -e '127.0.0.1 localhost\n' > vfs/etc/hosts
echo 'Содержимое системного лога.' > vfs/var/log/system.log
echo 'Содержимое лога приложения.' > vfs/var/log/app.log
echo -e '# Добро пожаловать в виртуальную файловую систему\nЭто тестовая ВФС.' > vfs/README.md
cd vfs 
zip -r ../test_vfs.zip ./*
cd ..
```
