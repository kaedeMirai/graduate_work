# Проектная работа: Кино вместе

## Где найти код? 

[Graduate work](https://github.com/Munewxar/graduate_work) - здесь хранится код дипломного проекта

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