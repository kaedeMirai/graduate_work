# Проект "Онлайн Кинотеатр"

## Сервис Watch Together

Репозиторий для дипломного проекта "Кино вместе", реализованного с использованием вебсокетов для синхронизации просмотра фильмов в реальном времени. Включает в себя синхронизированный чат и видеоплеер для комфортного просмотра фильмов в группе пользователей.

## Содержание:

- [Django Admin Panel](https://github.com/kaedeMirai/new_admin_panel_sprint_1) - **Панель администратора для управления контентом**
- [ETL](https://github.com/kaedeMirai/admin_panel_sprint_3) - **Перенос данных из PostgreSQL в ElasticSearch для реализации полнотекстового поиска.**
- [Auth](https://github.com/kaedeMirai/Auth_sprint_1-2) - **Аутентификация и авторизация пользователей на сайте с системой ролей.**
- [UGC](https://github.com/kaedeMirai/ugc_sprint_1) - **Сервис для удобного хранения аналитической информации и UGC.**
- [UGC +](https://github.com/kaedeMirai/ugc_sprint_2) - **Улучшение функционала UGC внедрением CI/CD процессов и настройкой системы логирования Setnry и ELK.**
- [Notification service](https://github.com/kaedeMirai/notifications_sprint_1) - **Отправка уведомлений пользователям о важных событиях и акциях в кинотеатре.**
- [Watch Together service](https://github.com/kaedeMirai/graduate_work) - **Позволяет пользователям смотреть фильмы совместно в реальном времени, обеспечивая синхронизацию видео и чата.**

## Где найти код? 

[Graduate work](https://github.com/kaedeMirai/graduate_work) - здесь хранится код дипломного проекта

# How-to: Вести локальную разработку

Создание виртуальной среды со всеми зависимостями
```shell
make venv
```

Сбилдить образ для разработки
```shell
make build_dev
```

Запустить docker-compose с запущенным сервисом
```shell
make run_dev
```

Запустить тесты. Тесты проходят локально 
```shell
make local_tests
```

# How-to: Запустить сервис с моками в работающем режиме

Скопировать .env.example в .env (либо переименовать .env.example) и заполнить их в следующих директориях:

корневая папка

/auth_service/

Создать сеть
```shell
make create_network
```
Сбилдить образы
```shell
make build_main
```
Запустить проект
```shell
make run_main
```

# How-to: Запустить фронтенд

Перейти в папку /frontend/app/
```shell
cd frontend/app
```

Установить зависимости
```shell
npm install
```

Запустить приложение
```shell
npm start
```

P.S. Для запуска фронтенд приложения необходимо превдварительно установить:
- **Nodejs**@latest
- **npm**@latest


# How-to: Тестирование через веб-интерфейс

1. Для входа используйте данные одного из тестовых пользователей:

**login**: anna001/sergey002/elena003/alexandr004/marina005/dmitriy006

**password**: anna001/sergey002/elena003/alexandr004/marina005/dmitriy006

2. Выберите друзей из списка и создайте сессию
3. Используйте видеоплеер и чат для тестирования функционала
4. Скопируйте ссылку сессии из строки браузера и перейдите по ссылке в другой вкладке/браузере.

Пример ссылки: http://localhost:3000/join_session?session_id=8cca0577-1c7d-4a81-8f57-f8f2b47aeff9

5. Взаимодействуйте с видеоплеером или чатом для тестирования функционала сервиса "Кино вместе"
