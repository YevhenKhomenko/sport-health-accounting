from django.db import models
from django.contrib.auth.models import User


class Organization(models.Model):
    organization_name = models.CharField("Назва організації", max_length=255)
    address = models.CharField("Адреса", max_length=255)
    phone = models.CharField("Телефон", max_length=50)
    email = models.EmailField("Email")
    type = models.CharField("Тип організації", max_length=100)
    organization_document = models.FileField("Документ організації", upload_to='organizations/', blank=True, null=True)

    def __str__(self):
        return self.organization_name


class Trainer(models.Model):
    last_name = models.CharField("Прізвище", max_length=100)
    first_name = models.CharField("Ім'я", max_length=100)
    patronymic = models.CharField("По батькові", max_length=100, blank=True, null=True)
    date_of_birth = models.DateField("Дата народження")
    gender = models.CharField("Стать", max_length=10)
    address = models.CharField("Домашня адреса", max_length=255)
    phone = models.CharField("Телефон", max_length=50)
    primary_sport = models.CharField("Основний вид спорту", max_length=100)
    additional_sports = models.CharField("Інші види спорту", max_length=255, blank=True, null=True)
    # Додаємо необов’язкове поле для організації тренера
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Організація",
        related_name="trainers"
    )

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Sportsperson(models.Model):
    last_name = models.CharField("Прізвище", max_length=100)
    first_name = models.CharField("Ім'я", max_length=100)
    patronymic = models.CharField("По батькові", max_length=100, blank=True, null=True)
    date_of_birth = models.DateField("Дата народження")
    gender = models.CharField("Стать", max_length=10)
    address = models.CharField("Домашня адреса", max_length=255)
    phone = models.CharField("Телефон", max_length=50)
    sports_category = models.CharField("Спортивний розряд", max_length=50)
    primary_sport = models.CharField("Основний вид спорту", max_length=100)
    additional_sports = models.CharField("Інші види спорту", max_length=255, blank=True, null=True)

    # Видаляємо null=True, оскільки ManyToMany поля не потребують його
    trainers = models.ManyToManyField(
        Trainer,
        through='SportspersonTrainer',
        blank=True,
        verbose_name="Тренери"
    )
    organizations = models.ManyToManyField(
        Organization,
        through='SportspersonOrganization',
        blank=True,
        verbose_name="Організації"
    )

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class SportspersonTrainer(models.Model):
    sportsperson = models.ForeignKey(Sportsperson, on_delete=models.CASCADE)
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Спортсмен – Тренер"
        verbose_name_plural = "Спортсмени – Тренери"


class SportspersonOrganization(models.Model):
    sportsperson = models.ForeignKey(Sportsperson, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Спортсмен – Організація"
        verbose_name_plural = "Спортсмени – Організації"


class MedicalRecord(models.Model):
    sportsperson = models.ForeignKey(
        Sportsperson,
        on_delete=models.CASCADE,
        related_name='medical_records',
        null=True,  # Keep null=True for now
        blank=True  # Add blank=True to allow empty values in forms
    )
    date_created = models.DateField("Дата створення карти")
    medical_facility = models.CharField("Медичний заклад", max_length=255)
    health_status = models.CharField("Стан здоров’я", max_length=100)
    diagnosis = models.CharField("Діагноз", max_length=255)
    functional_status = models.CharField("Функціональний статус", max_length=100, blank=True, null=True)
    physical_activity_group = models.CharField("Група для занять", max_length=100)
    admission_status = models.CharField("Допуск", max_length=50)
    medical_history = models.TextField("Історія хвороб", blank=True, null=True)
    medical_document = models.FileField("Медичний документ", upload_to='medical_documents/', blank=True, null=True)

    def __str__(self):
        return f"Медкарта {self.sportsperson} від {self.date_created}"


class Anthropometry(models.Model):
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='anthropometries')
    date_of_measurement = models.DateField("Дата вимірювання")
    weight = models.IntegerField("Вага (кг)")
    height = models.IntegerField("Зріст (см)")
    chest_circumference_inhale = models.IntegerField("Об’єм грудної клітки (вдих)")
    chest_circumference_exhale = models.IntegerField("Об’єм грудної клітки (видих)")
    chest_circumference_pause = models.IntegerField("Об’єм грудної клітки (пауза)")
    chest_circumference_difference = models.IntegerField("Різниця об’ємів")
    spirometry = models.IntegerField("Спірометрія")
    dynamometry_right = models.IntegerField("Динамометрія (права рука)")
    dynamometry_left = models.IntegerField("Динамометрія (ліва рука)")

    def __str__(self):
        return f"Антропометрія {self.medical_record} від {self.date_of_measurement}"


class AdditionalTests(models.Model):
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='additional_tests')
    ecg = models.CharField("ЕКГ", max_length=255, blank=True, null=True)
    physical_test_results = models.CharField("Результати фізичних тестів", max_length=255, blank=True, null=True)
    rufier_index = models.CharField("Проба Руф’є", max_length=100, blank=True, null=True)
    specialist_conclusion = models.CharField("Висновки спеціалістів", max_length=255, blank=True, null=True)
    ecg_file = models.FileField("Файл ЕКГ", upload_to='ecg_files/', blank=True, null=True)

    def __str__(self):
        return f"Додаткові тести для {self.medical_record}"


class Notes(models.Model):
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='notes')
    note = models.CharField("Примітка", max_length=500)
    note_file = models.FileField("Файл примітки", upload_to='notes_files/', blank=True, null=True)

    def __str__(self):
        return f"Примітка для {self.medical_record}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = (
        ('admin', 'Адміністратор'),
        ('editor', 'Редактор'),
        ('viewer', 'Переглядач'),
        ('pending', 'На розгляді'),
    )
    role = models.CharField("Роль", max_length=50, choices=ROLE_CHOICES, default='pending')

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class LoginLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Користувач")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Дата і час входу")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP-адреса")

    def __str__(self):
        return f"{self.user.username} - {self.timestamp}"

    