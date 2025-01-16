from fastapi import FastAPI, Form, Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from models import User, Computer
from database import SessionLocal, engine
import bcrypt
import os
import re

# Получаем путь к директории, в которой находится данный скрипт
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Статические файлы относительно директории проекта
static_files_path = os.path.join(BASE_DIR, "statics")

# Инициализация FastAPI приложения
app = FastAPI()

# Монтируем директорию с статическими файлами с использованием относительного пути
app.mount("/statics", StaticFiles(directory=static_files_path), name="statics")

# Конфигурация JWT
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Инициализация шаблонов и механизмов безопасности
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
templates = Jinja2Templates(directory="templates")

# Создание таблиц, если их нет
User.metadata.create_all(bind=engine)
Computer.metadata.create_all(bind=engine)

# Вспомогательные функции для работы с БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    # Преобразуем строку обратно в bytes для корректного сравнения
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')  # Преобразуем bytes в строку перед сохранением

def is_password_strong(password: str) -> bool:
    # Проверка на минимальную длину
    if len(password) < 8:
        return False
    
    # Проверка на наличие заглавной буквы
    if not re.search(r'[A-Z]', password):
        return False
    
    # Проверка на наличие цифры
    if not re.search(r'\d', password):
        return False
    
    # Проверка на наличие специального символа
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    
    return True

def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username.lower()).first()

def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="No authentication token found")
    
    try:
        # Извлекаем токен из формата "Bearer <token>"
        token = token.split(" ")[1]  # Извлекаем сам токен без "Bearer "
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Маршруты приложения
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

#@app.post("/register", response_class=HTMLResponse)
#async def register(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
#    db_user = get_user_by_username(db, username)
#    if db_user:
#        raise HTTPException(status_code=400, detail="Username already registered")
#    
#    hashed_password = get_password_hash(password)
#    new_user = User(username=username, password=hashed_password)
#    db.add(new_user)
#    db.commit()
#    db.refresh(new_user)
#    
#    return RedirectResponse("/login", status_code=303)

@app.post("/register", response_class=HTMLResponse)
async def register(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # Проверка, существует ли уже пользователь с таким именем
    db_user = get_user_by_username(db, username)
    if db_user:
        return templates.TemplateResponse("register.html", {
            "request": request, 
            "error_message": "Имя пользователя уже зарегистрированно"
        })
    
    # Проверка на сложность пароля
    if not is_password_strong(password):
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error_message": "Пароль слишком слабый. Он должен содержать не менее 8 символов, включая одну заглавную букву, одну цифру и один специальный символ."
        })
    
    # Хэшируем пароль
    hashed_password = get_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return RedirectResponse("/login", status_code=303)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        #raise HTTPException(status_code=401, detail="Неверные учетные данные")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error_message": "Неверный логин или пароль."
        })

    access_token = create_access_token(data={"sub": user.username})
    response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie(key="Authorization", value=f"Bearer {access_token}", httponly=True)
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    running_processes = ["Пример процесса", "Пример процесса1"]
    user_computers = db.query(Computer).filter_by(user_id=current_user.id).all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "processes": running_processes,
        "computers": user_computers,
        "current_user": current_user  # Передаем текущего пользователя
    })

@app.get("/shutdown", response_class=HTMLResponse)
async def shutdown():
    # Логика выключения компьютера
    print("shutdown process")
    return RedirectResponse("/dashboard", status_code=303)

@app.post("/logout")
async def logout(response: RedirectResponse):
    response.delete_cookie("Authorization")  # Удаляем cookie с токеном
    return RedirectResponse("/login", status_code=303)
