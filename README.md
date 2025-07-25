# monitoring_equipment
Web интерфейс для проверки оборудования мониторинга.
Python 3.9

# Запуск PEP8
python -m flake8

# Установка Nginx
1. Находясь на удалённом сервере, из любой директории выполните команду:
sudo apt install nginx -y 
2. Запустите Nginx командой:
sudo systemctl start nginx
3. Проверьте работу Nginx:
Введите в адресную строку браузера IP-адрес вашего удалённого сервера без указания порта. Должна открыться страница приветствия от Nginx


# Установка Docker Engine в Ubuntu
1. Скачайте и установите curl — консольную утилиту, которая умеет скачивать файлы по команде пользователя.
sudo apt update
sudo apt install curl
2. Перед первой установкой Docker Engine на новый хост-компьютер необходимо настроить aptрепозиторий Docker.
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
3. Чтобы установить последнюю версию, выполните:
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
4. Проверьте, что Docker работает:
sudo systemctl status docker 

# Перенос Docker хранилища на /var/log (данную папку также указываем в Docker Volume)
1. Остановим Docker 
sudo systemctl stop docker
2. Перемести текущую папку (если надо сохранить старые данные):
sudo mv /var/lib/docker /var/log/docker
Или если не нужно сохранять:
sudo rm -rf /var/lib/docker
sudo mkdir /var/log/docker
3. Создай симлинк:
sudo ln -s /var/log/docker /var/lib/docker
4. Убедись, что папка с нужными правами:
sudo chown -R root:root /var/log/docker
5. Запусти Docker снова:
sudo systemctl start docker
6. Проверьте хранилище Docker:
docker info | grep "Docker Root Dir"

# Запуск докер контейнера с базой данных:
1. Создайте volume для хранения данных PostgreSQL:
sudo docker volume create ts_core_db_data 
2. Создание и запуск БД в Docker контейнере с параметрами указанными в .env файле и хранением данных в Docker volume:
<!-- Для разработки мы откроем нужный нам порт, например 5432 хоста и перенаправим его на контейнер с портом 5432 (как в БД) -->
sudo docker run --name ts_core_db --env-file .env -v ts_core_db_data:/var/lib/postgresql/data -p 5432:5432 postgres:13.10
<!-- В продакшне мы свяжем чере Docker network контейнер БД и приложения -->
sudo docker run --name ts_core_db --env-file .env -v pg_data:/var/lib/postgresql/data postgres:13.10 

# Подготовка Docker network:
1. Чтобы Django мог из контейнера обратиться к серверу базы данных в другом контейнере, нужно объединить контейнеры в общую сеть.
sudo docker network create ts_core_network 
2. Присоединить к сети ts_core_network контейнер базы данных ts_core_db
sudo docker network connect ts_core_network ts_core_db

# Запуск web приложения через Docker:
1. Соберем образ приложения ts_core_backend:  
sudo docker build -t ts_core_backend . 
2. Контейнер будет обращаться к host.docker.internal:27018, а это будет проброшено на 127.0.0.1:27017 через socat
sudo apt install socat
sudo socat TCP-LISTEN:27018,fork TCP:127.0.0.1:27017
* Если хочешь, можно настроить это через docker-compose и проброс socat через отдельный контейнер — скажи, покажу как.
2. Запуск контейнера с Django-приложением (учитывая, что MongoDB слушает только на 127.0.0.1):
sudo docker run --env-file .env --net ts_core_network --name ts_core_backend_container --add-host=host.docker.internal:host-gateway -p 8000:8000 ts_core_backend


<!-- Т.к. MongoDB у тебя запущена локально на хосте и слушает только на 127.0.0.1 (localhost), Docker-контейнер не видит её на localhost контейнера. -->
<!-- Решение — запускать Django контейнер с сетью хоста, чтобы localhost в контейнере совпадал с localhost на хосте. -->
<!-- sudo docker run --net=host --env-file .env --name ts_core_backend_container ts_core_backend -->
<!-- sudo docker run -d --name ts_core_backend_container --env-file .env --add-host=host.docker.internal:host-gateway -p 8000:8000 ts_core_backend -->
<!-- apt update && apt install -y nano -->

sudo docker container stop ts_core_backend_container && sudo docker container rm ts_core_backend_container && sudo docker image rm ts_core_backend