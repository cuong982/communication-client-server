# README file
alembic init migrations
alembic revision --autogenerate -m "create messages table"
alembic upgrade head