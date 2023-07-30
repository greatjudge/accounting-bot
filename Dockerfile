# базовый образ
FROM python:3.10
LABEL authors="greatjudge"

# Создем папку accounting-bot и устанавливаем рабочий каталог контейнера
WORKDIR /accounting-bot

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt ./
# Устанавливаем библиотеки из requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем все файлы из локального проекта в контейнер
COPY . ./

RUN alembic

ENTRYPOINT ["python", "bot.py"]
