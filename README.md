# parental_control_server
- docker pull postgres
- docker run --name my_postgres -e POSTGRES_PASSWORD=mysecretpassword -d -p 5432:5432 postgres
- docker-compose up -d
- запуск проекта на fast api:
    - cd web_monitor 
    - uvicorn app:app --reload --host 0.0.0.0 --port 8001
    - uvicorn app:app --reload
    - docker volume
    - docker volume rm
    