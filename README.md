git clone <repository-url>
cd sport_accounting/sport_accounting

Generate SECRET_KEY:
python -c "import secrets; print(secrets.token_urlsafe(50))"

nano .env

.env:
SECRET_KEY=your-secure-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://sport_user:sport_password@db:5432/sport_accounting
DB_NAME=sport_accounting
DB_USER=sport_user
DB_PASSWORD=sport_password

docker-compose build
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

docker-compose down
