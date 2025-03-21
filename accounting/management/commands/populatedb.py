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

        # Створення організацій
        org_names = [
            "ФК 'Полтава'",
            "Спортшкола 'Горизонт'",
            "Спортивна школа 'Авангард'",
            "Клуб 'Енергія'"
        ]
        organizations = []
        for name in org_names:
            org = Organization.objects.create(
                organization_name=name,
                type="Спортивна організація" if "ФК" in name or "Клуб" in name else "Освітня організація",
                address=f"м. Полтава, вул. {name.split()[0]} 10",
                phone="380501234567",
                email=f"{name.split()[0].lower()}@example.com"
            )
            organizations.append(org)
        self.stdout.write(f"Створено {len(organizations)} організацій.")

        # Створення тренерів
        trainer_data = [
            {"last_name": "Коваленко", "first_name": "Іван", "patronymic": "Петрович", "date_of_birth": date(1980, 5, 20), "gender": "male", "address": "м. Полтава, вул. Тренерська, 1", "phone": "380501112233", "primary_sport": "Футбол", "additional_sports": "Біг"},
            {"last_name": "Сидоренко", "first_name": "Марія", "patronymic": "Іванівна", "date_of_birth": date(1985, 7, 15), "gender": "female", "address": "м. Полтава, вул. Спортивна, 2", "phone": "380507776655", "primary_sport": "Волейбол", "additional_sports": ""},
            {"last_name": "Петров", "first_name": "Олександр", "patronymic": "Сергійович", "date_of_birth": date(1975, 3, 10), "gender": "male", "address": "м. Полтава, вул. Зіркова, 5", "phone": "380507888999", "primary_sport": "Баскетбол", "additional_sports": "Швидкість"},
            {"last_name": "Мельник", "first_name": "Олена", "patronymic": "Василівна", "date_of_birth": date(1990, 8, 30), "gender": "female", "address": "м. Полтава, вул. Садова, 3", "phone": "380506667788", "primary_sport": "Легка атлетика", "additional_sports": ""}
        ]
        trainers = []
        for data in trainer_data:
            trainer = Trainer.objects.create(**data)
            # Додаємо тренеру випадкову організацію (не обов’язково)
            trainer.organization = random.choice(organizations)
            trainer.save()
            trainers.append(trainer)
        self.stdout.write(f"Створено {len(trainers)} тренерів.")

        # Створення спортсменів
        sportsperson_data = [
            {"last_name": "Іванов", "first_name": "Олександр", "patronymic": "Сергійович", "date_of_birth": date(2000, 1, 10), "gender": "male", "address": "м. Полтава, вул. Центральна, 12", "phone": "380501234000", "sports_category": "Професійний", "primary_sport": "Футбол", "additional_sports": "Біг"},
            {"last_name": "Петренко", "first_name": "Олена", "patronymic": "Володимирівна", "date_of_birth": date(1998, 3, 5), "gender": "female", "address": "м. Полтава, вул. Лісова, 8", "phone": "380509876000", "sports_category": "Аматорський", "primary_sport": "Волейбол", "additional_sports": ""},
            {"last_name": "Смирнов", "first_name": "Дмитро", "patronymic": "Іванович", "date_of_birth": date(2002, 6, 20), "gender": "male", "address": "м. Полтава, вул. Промислова, 5", "phone": "380501112345", "sports_category": "Аматорський", "primary_sport": "Баскетбол", "additional_sports": "Футбол"},
            {"last_name": "Коваленко", "first_name": "Марія", "patronymic": "Олександрівна", "date_of_birth": date(1999, 12, 1), "gender": "female", "address": "м. Полтава, вул. Головна, 7", "phone": "380509998877", "sports_category": "Професійний", "primary_sport": "Легка атлетика", "additional_sports": ""}
        ]
        sportspersons = []
        for data in sportsperson_data:
            sp = Sportsperson.objects.create(**data)
            # Прив'яжемо випадкових тренерів та організації
            sp.trainers.add(random.choice(trainers))
            sp.organizations.add(random.choice(organizations))
            sportspersons.append(sp)
        self.stdout.write(f"Створено {len(sportspersons)} спортсменів.")

        # Створення медичних записів для кожного спортсмена (2 записи на спортсмена)
        medical_records = []
        for sp in sportspersons:
            for i in range(2):
                mr = MedicalRecord.objects.create(
                    sportsperson=sp,
                    date_created=timezone.now() - timedelta(days=random.randint(0, 30)),
                    medical_facility=random.choice([
                        "Полтавський медичний центр",
                        "Полтавська клініка",
                        "Дитяча поліклініка"
                    ]),
                    health_status=random.choice(["Здоровий", "Легкий дискомфорт", "Поганий"]),
                    diagnosis=random.choice(["Немає", "М'язовий розтяг", "Пошкодження зв’язок"]),
                    functional_status=random.choice(["Нормальний", "Обмежений"]),
                    physical_activity_group=random.choice(["A", "B", "C"]),
                    admission_status=random.choice(["Допущений", "Не допущений"]),
                    medical_history=random.choice(["Немає", "Нещодавня травма", "Хронічне захворювання"])
                )
                medical_records.append(mr)
        self.stdout.write(f"Створено {len(medical_records)} медичних записів.")

        # Створення антропометричних даних для кожного медичного запису (1 запис на мед. запис)
        anthropometries = []
        for mr in medical_records:
            anthro = Anthropometry.objects.create(
                medical_record=mr,
                date_of_measurement=mr.date_created.date(),
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
                ecg=random.choice(["Норма", "Відхилення"]),
                physical_test_results=random.choice(["Відмінно", "Добре", "Задовільно"]),
                rufier_index=str(random.randint(1, 10)),
                specialist_conclusion=random.choice(["Все гаразд", "Потрібен додатковий огляд"])
            )
            additional_tests.append(at)
        self.stdout.write(f"Створено {len(additional_tests)} записів додаткових обстежень.")

        # Створення приміток для кожного медичного запису (1 примітка)
        notes_list = []
        for mr in medical_records:
            note = Notes.objects.create(
                medical_record=mr,
                note=random.choice([
                    "Регулярний огляд, немає зауважень.",
                    "Потрібен додатковий огляд.",
                    "Змін у стані немає."
                ])
            )
            notes_list.append(note)
        self.stdout.write(f"Створено {len(notes_list)} приміток.")

        self.stdout.write(self.style.SUCCESS("Базу даних заповнено тестовими даними."))
