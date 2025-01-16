# parental_control_server
**Запуск БД:**
<br>
`docker pull postgres`
<br>
`docker run --name my_postgres -e POSTGRES_PASSWORD=mysecretpassword -d -p 5432:5432 postgres`
<br>
`docker-compose up -d`

**Запуск проекта на fast api:**
<br>
`cd web_monitor`
<br> 
`uvicorn app:app --reload --host 0.0.0.0 --port 8000`
<br>
`uvicorn app:app --reload`
<br>
или
<br>
`fastapi dev app.py`
<br>
Если порт занят
<br>
`lsof -i :8000`
<br>
`kill -9 PID_процесса`

**Очистить БД (при необходимости):**
<br>
`docker volume`
<br>
`docker volume rm`
    