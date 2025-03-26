# accounting/management/commands/populatedb.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random
from accounting.models import (
    Organization, Trainer, Sportsperson,
    MedicalRecord, Anthropometry, AdditionalTests, Notes
)

class Command(BaseCommand):
    help = "Заповнення бази даних тестовими даними (попередні дані видаляються)"

    def handle(self, *args, **options):
        self.stdout.write("Видаляємо попередні дані з бази даних...")
        # Видаляємо дані в правильному порядку (починаючи з дочірніх моделей)
        Notes.objects.all().delete()
        AdditionalTests.objects.all().delete()
        Anthropometry.objects.all().delete()
        MedicalRecord.objects.all().delete()
        # Many-to-many записи будуть видалені автоматично
        Sportsperson.objects.all().delete()
        Trainer.objects.all().delete()
        Organization.objects.all().delete()
        self.stdout.write("Попередні дані видалено.")

        self.stdout.write("Починаємо заповнення бази даних тестовими даними...")

        # Створення організацій (10 організацій)
        org_names = [
            "ФК 'Динамо'",
            "Спортшкола 'Олімп'",
            "Спортивна школа 'Зірка'",
            "Клуб 'Енергія'",
            "ФК 'Вікторія'",
            "Школа 'Майбутнє'",
            "Клуб 'Сила'",
            "Спортшкола 'Гармонія'",
            "ФК 'Легіон'",
            "Спортивний центр 'Прогрес'"
        ]
        organizations = []
        for name in org_names:
            org = Organization.objects.create(
                organization_name=name,
                type="Спортивна організація" if "ФК" in name or "Клуб" in name else "Освітня організація",
                address=f"м. Полтава, вул. {name.split()[0]} {random.randint(1, 50)}",
                phone=f"38050{random.randint(1000000, 9999999)}",
                email=f"{name.split()[0].lower()}@example.com",
                organization_document=None  # Можна додати фіктивний файл, якщо потрібно
            )
            organizations.append(org)
        self.stdout.write(f"Створено {len(organizations)} організацій.")

        # Створення тренерів (15 тренерів)
        trainer_data = [
            {"last_name": "Коваленко", "first_name": "Іван", "patronymic": "Петрович", "date_of_birth": date(1980, 5, 20), "gender": "male", "address": "м. Полтава, вул. Тренерська, 1", "phone": "380501112233", "primary_sport": "Футбол", "additional_sports": "Біг"},
            {"last_name": "Сидоренко", "first_name": "Марія", "patronymic": "Іванівна", "date_of_birth": date(1985, 7, 15), "gender": "female", "address": "м. Полтава, вул. Спортивна, 2", "phone": "380507776655", "primary_sport": "Волейбол", "additional_sports": "Плавання"},
            {"last_name": "Петров", "first_name": "Олександр", "patronymic": "Сергійович", "date_of_birth": date(1975, 3, 10), "gender": "male", "address": "м. Полтава, вул. Зіркова, 5", "phone": "380507888999", "primary_sport": "Баскетбол", "additional_sports": "Швидкість"},
            {"last_name": "Мельник", "first_name": "Олена", "patronymic": "Василівна", "date_of_birth": date(1990, 8, 30), "gender": "female", "address": "м. Полтава, вул. Садова, 3", "phone": "380506667788", "primary_sport": "Легка атлетика", "additional_sports": ""},
            {"last_name": "Бондаренко", "first_name": "Сергій", "patronymic": "Олегович", "date_of_birth": date(1982, 11, 12), "gender": "male", "address": "м. Полтава, вул. Центральна, 15", "phone": "380509876543", "primary_sport": "Футбол", "additional_sports": "Теніс"},
            {"last_name": "Литвиненко", "first_name": "Анна", "patronymic": "Михайлівна", "date_of_birth": date(1988, 4, 25), "gender": "female", "address": "м. Полтава, вул. Лісова, 7", "phone": "380501234567", "primary_sport": "Гімнастика", "additional_sports": "Йога"},
            {"last_name": "Шевченко", "first_name": "Віктор", "patronymic": "Іванович", "date_of_birth": date(1978, 9, 5), "gender": "male", "address": "м. Полтава, вул. Сонячна, 10", "phone": "380507654321", "primary_sport": "Бокс", "additional_sports": "Біг"},
            {"last_name": "Григоренко", "first_name": "Юлія", "patronymic": "Олександрівна", "date_of_birth": date(1992, 2, 18), "gender": "female", "address": "м. Полтава, вул. Польова, 4", "phone": "380509123456", "primary_sport": "Плавання", "additional_sports": "Волейбол"},
            {"last_name": "Ткаченко", "first_name": "Максим", "patronymic": "Васильович", "date_of_birth": date(1983, 6, 30), "gender": "male", "address": "м. Полтава, вул. Квіткова, 8", "phone": "380501987654", "primary_sport": "Теніс", "additional_sports": "Футбол"},
            {"last_name": "Даниленко", "first_name": "Наталія", "patronymic": "Сергіївна", "date_of_birth": date(1987, 12, 1), "gender": "female", "address": "м. Полтава, вул. Зелена, 12", "phone": "380507123456", "primary_sport": "Легка атлетика", "additional_sports": "Біг"},
            {"last_name": "Кравченко", "first_name": "Олег", "patronymic": "Миколайович", "date_of_birth": date(1979, 8, 15), "gender": "male", "address": "м. Полтава, вул. Мирна, 3", "phone": "380509456123", "primary_sport": "Баскетбол", "additional_sports": "Плавання"},
            {"last_name": "Зайченко", "first_name": "Ірина", "patronymic": "Вікторівна", "date_of_birth": date(1991, 3, 22), "gender": "female", "address": "м. Полтава, вул. Весняна, 6", "phone": "380501654987", "primary_sport": "Гімнастика", "additional_sports": "Йога"},
            {"last_name": "Мороз", "first_name": "Андрій", "patronymic": "Олександрович", "date_of_birth": date(1981, 10, 10), "gender": "male", "address": "м. Полтава, вул. Осіння, 9", "phone": "380507789456", "primary_sport": "Футбол", "additional_sports": "Теніс"},
            {"last_name": "Левченко", "first_name": "Софія", "patronymic": "Ігорівна", "date_of_birth": date(1989, 5, 8), "gender": "female", "address": "м. Полтава, вул. Літня, 11", "phone": "380509321654", "primary_sport": "Волейбол", "additional_sports": "Плавання"},
            {"last_name": "Романенко", "first_name": "Владислав", "patronymic": "Дмитрович", "date_of_birth": date(1984, 1, 25), "gender": "male", "address": "м. Полтава, вул. Зимова, 2", "phone": "380501456789", "primary_sport": "Бокс", "additional_sports": "Біг"}
        ]
        trainers = []
        for data in trainer_data:
            trainer = Trainer.objects.create(**data)
            # Додаємо тренеру випадкову організацію
            trainer.organization = random.choice(organizations)
            trainer.save()
            trainers.append(trainer)
        self.stdout.write(f"Створено {len(trainers)} тренерів.")

        # Створення спортсменів (20 спортсменів)
        sportsperson_data = [
            {"last_name": "Іванов", "first_name": "Олександр", "patronymic": "Сергійович", "date_of_birth": date(2000, 1, 10), "gender": "male", "address": "м. Полтава, вул. Центральна, 12", "phone": "380501234000", "sports_category": "Професійний", "primary_sport": "Футбол", "additional_sports": "Біг"},
            {"last_name": "Петренко", "first_name": "Олена", "patronymic": "Володимирівна", "date_of_birth": date(1998, 3, 5), "gender": "female", "address": "м. Полтава, вул. Лісова, 8", "phone": "380509876000", "sports_category": "Аматорський", "primary_sport": "Волейбол", "additional_sports": "Плавання"},
            {"last_name": "Смирнов", "first_name": "Дмитро", "patronymic": "Іванович", "date_of_birth": date(2002, 6, 20), "gender": "male", "address": "м. Полтава, вул. Промислова, 5", "phone": "380501112345", "sports_category": "Аматорський", "primary_sport": "Баскетбол", "additional_sports": "Футбол"},
            {"last_name": "Коваленко", "first_name": "Марія", "patronymic": "Олександрівна", "date_of_birth": date(1999, 12, 1), "gender": "female", "address": "м. Полтава, вул. Головна, 7", "phone": "380509998877", "sports_category": "Професійний", "primary_sport": "Легка атлетика", "additional_sports": "Біг"},
            {"last_name": "Бондар", "first_name": "Віктор", "patronymic": "Михайлович", "date_of_birth": date(2001, 4, 15), "gender": "male", "address": "м. Полтава, вул. Сонячна, 3", "phone": "380501234567", "sports_category": "Професійний", "primary_sport": "Бокс", "additional_sports": "Теніс"},
            {"last_name": "Литвин", "first_name": "Анна", "patronymic": "Петрівна", "date_of_birth": date(2003, 8, 22), "gender": "female", "address": "м. Полтава, вул. Польова, 9", "phone": "380509876543", "sports_category": "Аматорський", "primary_sport": "Гімнастика", "additional_sports": "Йога"},
            {"last_name": "Шевчук", "first_name": "Ігор", "patronymic": "Васильович", "date_of_birth": date(1997, 11, 30), "gender": "male", "address": "м. Полтава, вул. Квіткова, 4", "phone": "380507654321", "sports_category": "Професійний", "primary_sport": "Плавання", "additional_sports": "Волейбол"},
            {"last_name": "Григоренко", "first_name": "Софія", "patronymic": "Олегівна", "date_of_birth": date(2000, 2, 18), "gender": "female", "address": "м. Полтава, вул. Зелена, 6", "phone": "380509123456", "sports_category": "Аматорський", "primary_sport": "Теніс", "additional_sports": "Футбол"},
            {"last_name": "Ткач", "first_name": "Максим", "patronymic": "Іванович", "date_of_birth": date(1999, 7, 10), "gender": "male", "address": "м. Полтава, вул. Мирна, 2", "phone": "380501987654", "sports_category": "Професійний", "primary_sport": "Футбол", "additional_sports": "Біг"},
            {"last_name": "Данилюк", "first_name": "Наталія", "patronymic": "Сергіївна", "date_of_birth": date(2001, 9, 5), "gender": "female", "address": "м. Полтава, вул. Весняна, 8", "phone": "380507123456", "sports_category": "Аматорський", "primary_sport": "Легка атлетика", "additional_sports": "Плавання"},
            {"last_name": "Кравець", "first_name": "Олег", "patronymic": "Миколайович", "date_of_birth": date(1998, 5, 12), "gender": "male", "address": "м. Полтава, вул. Осіння, 10", "phone": "380509456123", "sports_category": "Професійний", "primary_sport": "Баскетбол", "additional_sports": "Теніс"},
            {"last_name": "Зайцев", "first_name": "Ірина", "patronymic": "Вікторівна", "date_of_birth": date(2002, 3, 25), "gender": "female", "address": "м. Полтава, вул. Літня, 5", "phone": "380501654987", "sports_category": "Аматорський", "primary_sport": "Гімнастика", "additional_sports": "Йога"},
            {"last_name": "Морозов", "first_name": "Андрій", "patronymic": "Олександрович", "date_of_birth": date(1997, 10, 15), "gender": "male", "address": "м. Полтава, вул. Зимова, 7", "phone": "380507789456", "sports_category": "Професійний", "primary_sport": "Бокс", "additional_sports": "Біг"},
            {"last_name": "Левчук", "first_name": "Юлія", "patronymic": "Ігорівна", "date_of_birth": date(2000, 6, 8), "gender": "female", "address": "м. Полтава, вул. Центральна, 15", "phone": "380509321654", "sports_category": "Аматорський", "primary_sport": "Волейбол", "additional_sports": "Плавання"},
            {"last_name": "Романчук", "first_name": "Владислав", "patronymic": "Дмитрович", "date_of_birth": date(1999, 1, 20), "gender": "male", "address": "м. Полтава, вул. Лісова, 3", "phone": "380501456789", "sports_category": "Професійний", "primary_sport": "Футбол", "additional_sports": "Теніс"},
            {"last_name": "Савчук", "first_name": "Катерина", "patronymic": "Олександрівна", "date_of_birth": date(2001, 12, 10), "gender": "female", "address": "м. Полтава, вул. Промислова, 8", "phone": "380509654321", "sports_category": "Аматорський", "primary_sport": "Легка атлетика", "additional_sports": "Біг"},
            {"last_name": "Мельничук", "first_name": "Павло", "patronymic": "Вікторович", "date_of_birth": date(1998, 8, 30), "gender": "male", "address": "м. Полтава, вул. Головна, 4", "phone": "380507321654", "sports_category": "Професійний", "primary_sport": "Баскетбол", "additional_sports": "Плавання"},
            {"last_name": "Гончар", "first_name": "Оксана", "patronymic": "Михайлівна", "date_of_birth": date(2002, 4, 5), "gender": "female", "address": "м. Полтава, вул. Сонячна, 6", "phone": "380509123987", "sports_category": "Аматорський", "primary_sport": "Гімнастика", "additional_sports": "Йога"},
            {"last_name": "Козлов", "first_name": "Євген", "patronymic": "Олегович", "date_of_birth": date(1997, 2, 15), "gender": "male", "address": "м. Полтава, вул. Польова, 2", "phone": "380501789456", "sports_category": "Професійний", "primary_sport": "Бокс", "additional_sports": "Біг"},
            {"last_name": "Білоус", "first_name": "Аліна", "patronymic": "Сергіївна", "date_of_birth": date(2000, 9, 25), "gender": "female", "address": "м. Полтава, вул. Квіткова, 9", "phone": "380507456123", "sports_category": "Аматорський", "primary_sport": "Волейбол", "additional_sports": "Плавання"}
        ]
        sportspersons = []
        for data in sportsperson_data:
            sp = Sportsperson.objects.create(**data)
            # Прив'яжемо 1-3 випадкових тренерів
            num_trainers = random.randint(1, 3)
            selected_trainers = random.sample(trainers, num_trainers)
            for trainer in selected_trainers:
                sp.trainers.add(trainer)
            # Прив'яжемо 1-2 випадкові організації
            num_orgs = random.randint(1, 2)
            selected_orgs = random.sample(organizations, num_orgs)
            for org in selected_orgs:
                sp.organizations.add(org)
            sportspersons.append(sp)
        self.stdout.write(f"Створено {len(sportspersons)} спортсменів.")

        # Створення медичних записів для кожного спортсмена (2-3 записи на спортсмена)
        medical_records = []
        for sp in sportspersons:
            num_records = random.randint(2, 3)  # 2 або 3 медичні записи
            for i in range(num_records):
                mr = MedicalRecord.objects.create(
                    sportsperson=sp,
                    date_created=timezone.now() - timedelta(days=random.randint(0, 365)),  # Останній рік
                    medical_facility=random.choice([
                        "Полтавський медичний центр",
                        "Полтавська клініка",
                        "Дитяча поліклініка",
                        "Медцентр 'Здоров’я'",
                        "Клініка 'МедЕксперт'"
                    ]),
                    health_status=random.choice(["Здоровий", "Легкий дискомфорт", "Поганий", "Стабільний"]),
                    diagnosis=random.choice(["Немає", "М'язовий розтяг", "Пошкодження зв’язок", "Запалення", "Перевтома"]),
                    functional_status=random.choice(["Нормальний", "Обмежений", "Знижений"]),
                    physical_activity_group=random.choice(["A", "B", "C", "D"]),
                    admission_status=random.choice(["Допущений", "Не допущений", "Умовно допущений"]),
                    medical_history=random.choice(["Немає", "Нещодавня травма", "Хронічне захворювання", "Алергія"])
                )
                medical_records.append(mr)
        self.stdout.write(f"Створено {len(medical_records)} медичних записів.")

        # Створення антропометричних даних для кожного медичного запису (1-2 записи на мед. запис)
        anthropometries = []
        for mr in medical_records:
            num_anthro = random.randint(1, 2)  # 1 або 2 антропометричні записи
            for i in range(num_anthro):
                anthro = Anthropometry.objects.create(
                    medical_record=mr,
                    sportsperson=mr.sportsperson,  # Додаємо sportsperson
                    date_of_measurement=mr.date_created.date() - timedelta(days=random.randint(0, 10)),
                    weight=random.randint(50, 100),
                    height=random.randint(150, 200),
                    chest_circumference_inhale=random.randint(80, 110),
                    chest_circumference_exhale=random.randint(70, 100),
                    chest_circumference_pause=random.randint(75, 105),
                    chest_circumference_difference=random.randint(5, 15),
                    spirometry=random.randint(80, 120),
                    dynamometry_right=random.randint(30, 60),
                    dynamometry_left=random.randint(30, 60)
                )
                anthropometries.append(anthro)
        self.stdout.write(f"Створено {len(anthropometries)} записів антропометрії.")

        # Створення додаткових обстежень для кожного медичного запису (1 запис)
        additional_tests = []
        for mr in medical_records:
            at = AdditionalTests.objects.create(
                medical_record=mr,
                sportsperson=mr.sportsperson,  # Додаємо sportsperson
                ecg=random.choice(["Норма", "Відхилення", "Тахікардія", "Аритмія"]),
                physical_test_results=random.choice(["Відмінно", "Добре", "Задовільно", "Незадовільно"]),
                rufier_index=str(random.randint(1, 15)),
                specialist_conclusion=random.choice(["Все гаразд", "Потрібен додатковий огляд", "Рекомендується відпочинок", "Призначено лікування"]),
                ecg_file=None  # Можна додати фіктивний файл, якщо потрібно
            )
            additional_tests.append(at)
        self.stdout.write(f"Створено {len(additional_tests)} записів додаткових обстежень.")

        # Створення приміток для кожного медичного запису (1-2 примітки)
        notes_list = []
        for mr in medical_records:
            num_notes = random.randint(1, 2)  # 1 або 2 примітки
            for i in range(num_notes):
                note = Notes.objects.create(
                    medical_record=mr,
                    sportsperson=mr.sportsperson,  # Додаємо sportsperson
                    note=random.choice([
                        "Регулярний огляд, немає зауважень.",
                        "Потрібен додатковий огляд.",
                        "Змін у стані немає.",
                        "Рекомендується зменшити навантаження.",
                        "Спостерігається покращення."
                    ]),
                    note_file=None  # Можна додати фіктивний файл, якщо потрібно
                )
                notes_list.append(note)
        self.stdout.write(f"Створено {len(notes_list)} приміток.")

        self.stdout.write(self.style.SUCCESS("Базу даних заповнено тестовими даними."))