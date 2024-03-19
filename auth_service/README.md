# Где найти код?
1. [Auth API](https://github.com/Munewxar/Auth_sprint_1) - здесь хранится код auth api
2. [Async API](https://github.com/Munewxar/Async_API_sprint_1) - здесь хранится код async api
3. [Admin panel](https://github.com/Munewxar/new_admin_panel_sprint_2) - здесь хранится код admin panel

# Ссылка на документацию api
1. http://localhost:8000/api/openapi#

# Инструкция по запуску проекта
1. Склонировать репозиторий

   ```
   git clone https://github.com/Munewxar/Auth_sprint_1.git
   ```
2. Скопировать .env.example в .env (либо переименовать .env.example) и заполнить его
4. В командной строке запустить проект

    ```
    make venv
    make build_image
    make run_dev
    ```
5. Создание superuser:
   
   ```
   make create_super_user
   ```
