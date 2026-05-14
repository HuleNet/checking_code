Сначала надо создать .env-файлы, шаблоны есть у сервисов.

docker compose --profile judge up --build -d - запустить 
docker compose --profile judge down - закрыть
docker compose --profile judge down -v - закрыть и удалить volumes

Если это первый запуск или до этого была выполнена команда docker compose --profile judge down -v - закрыть и удалить volumes:
docker compose exec task_service uv run alembic upgrade head
docker compose exec checking_service uv run alembic upgrade head

localhost:8001 - task_service
localhost:8002 - checking_service
