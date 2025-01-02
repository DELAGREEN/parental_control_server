# parental_control_server
Запуск БД:
- docker pull postgres
- docker run --name my_postgres -e POSTGRES_PASSWORD=mysecretpassword -d -p 5432:5432 postgres
- docker-compose up -d

Запуск проекта на fast api:
- cd web_monitor 
- uvicorn app:app --reload --host 0.0.0.0 --port 8000
- uvicorn app:app --reload

    ИЛИ
- fastapi dev app.py

Очистить БД
- docker volume
- docker volume rm
    