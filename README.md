# Сервис tfidf 

Сервис tfidf .



## Требования:

Установите необходимое программное обеспечение:

1. [Docker Desktop](https://www.docker.com).
2. [Git](https://github.com/git-guides/install-git).
3. [PyCharm](https://www.jetbrains.com/ru-ru/pycharm/download) (optional).

## Установка

Клонируйте репозиторий на ваш компьютер.

1. Для настройки приложения скопируйте файл `.env.sample` в файл `.env`:
    ```shell
    cp .env.sample .env
    ```
   
    Этот файл содержит переменные окружения, которые будут использоваться в приложении. Примерный файл `.env.sample`) содержит набор переменных с настройками по умолчанию. Его можно настроить в зависимости от окружения.

2. Постройте контейнер с помощью Docker Compose:
    ```shell
    docker compose build
    ```
    Эта команда должна быть выполнена из корневой директории, где находится `Dockerfile` .
    Также нужно будет заново построить контейнер, если вы обновили `requirements.txt`.

3. Для корректной работы приложения настройте базу данных. Примените миграции для создания таблиц в базе данных:
    ```shell
    docker compose run table-reservation-app alembic upgrade head
    ```

4. Теперь можно запустить проект внутри Docker контейнера:
    ```shell
    docker compose up
    ```
   Когда контейнеры будут запущены, сервер начнёт работать по адресу [http://0.0.0.0:8010/docs](http://0.0.0.0:8010/docs). Вы можете открыть его в браузере.

## Использование

### Миграции

Для первоначальной настройки функционала миграций выполните команду:
```bash
docker compose exec table-reservation-app alembic init -t async migrations
```
Эта команда создаст директорию с конфигурационными файлами для настройки функционала асинхронных миграций.

Для создания новых миграций, которые обновят таблицы базы данных в соответствии с обновлёнными моделями, выполните команду:
```bash
docker compose run table-reservation-app alembic revision --autogenerate  -m "your description"
```

Чтобы применить созданные миграции, выполните:
```bash
docker compose run table-reservation-app alembic upgrade head
```

### Автоматизированные команды

Проект содержит специальный `Makefile` который предоставляет ярлыки для набора команд:
1. Построить Docker контейнер:
    ```shell
    make build
    ```

2. Сгенерировать документацию Sphinx:
    ```shell
    make docs-html
    ```

3. Автоформатировать исходный код:
    ```shell
    make format
    ```

4. Статический анализ (линтеры):
    ```shell
    make lint
    ```


6. Run autoformat, linters and tests in one command:
    ```shell
    make all
    ```

Запускайте эти команды из исходной директории, где находится `Makefile`.

## Документация

Проект интегрирован с системой документации [Sphinx](https://www.sphinx-doc.org/en/master/) Она позволяет создавать документацию из исходного кода. Исходный код должен содержать docstring'и в формате [reStructuredText](https://docutils.sourceforge.io/rst.html) .

Чтобы создать HTML документацию, выполните команду из исходной директории, где находится `Makefile`:
```shell
make docs-html
```

После генерации документацию можно открыть из файла `docs/build/html/index.html`.

## License
[MIT](https://choosealicense.com/licenses/mit/)
