from django.db import models
from django.contrib.auth.models import User


class Organization(models.Model):
    organization_name = models.CharField("Назва організації", max_length=255)
    address = models.CharField("Адреса", max_length=255, blank=True)
    phone = models.CharField("Телефон", max_length=50, blank=True)
    email = models.EmailField("Email", blank=True)
    type = models.CharField("Тип організації", max_length=100, blank=True)

    def __str__(self):
        return self.organization_name


class Trainer(models.Model):
    last_name = models.CharField("Прізвище", max_length=100)
    first_name = models.CharField("Ім'я", max_length=100, blank=True)
    patronymic = models.CharField("По батькові", max_length=100, blank=True, null=True)
    phone = models.CharField("Телефон", max_length=50, blank=True)
    primary_sport = models.CharField("Основний вид спорту", max_length=100)
    additional_sports = models.CharField("Інші види спорту", max_length=255, blank=True, null=True)
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
    date_of_birth = models.DateField("Дата народження", blank=True, null=True)
    GENDER_CHOICES = (
        ('Чоловік', 'Чоловік'),
        ('Жінка', 'Жінка'),
    )
    gender = models.CharField("Стать", max_length=10, choices=GENDER_CHOICES)
    address = models.CharField("Домашня адреса", max_length=255, blank=True)
    phone = models.CharField("Телефон", max_length=50, blank=True)
    sports_category = models.CharField("Спортивний розряд", max_length=50)
    primary_sport = models.CharField("Основний вид спорту", max_length=100)
    additional_sports = models.CharField("Інші види спорту", max_length=255, blank=True, null=True)

    trainers = models.ManyToManyField(Trainer, through='SportspersonTrainer', blank=True, verbose_name="Тренери")
    organizations = models.ManyToManyField(Organization, through='SportspersonOrganization', blank=True, verbose_name="Організації")

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
        null=True,
        blank=True
    )
    date_created = models.DateField("Дата створення карти")
    medical_facility = models.CharField("Медичний заклад", max_length=255, blank=True)
    health_status = models.CharField("Стан здоров’я", max_length=100, blank=True)
    diagnosis = models.CharField("Діагноз", max_length=255, blank=True)
    functional_status = models.CharField("Функціональний статус", max_length=100, blank=True, null=True)
    physical_activity_group = models.CharField("Група для занять", max_length=100, blank=True)
    admission_status = models.CharField("Допуск", max_length=50, blank=True)
    medical_history = models.TextField("Історія хвороб", blank=True, null=True)
    medical_document = models.BinaryField("Медичний документ", blank=True, null=True)
    medical_document_name = models.CharField("Назва файлу медичного документа", max_length=255, blank=True, null=True)
    medical_document_mime_type = models.CharField("MIME-тип медичного документа", max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Медкарта {self.sportsperson} від {self.date_created}"


class Anthropometry(models.Model):
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='anthropometries')
    sportsperson = models.ForeignKey(
        Sportsperson,
        on_delete=models.CASCADE,
        related_name='sportsperson_anthropometries',
        null=True,
        blank=True
    )
    date_of_measurement = models.DateField("Дата вимірювання", blank=True, null=True)
    weight = models.FloatField("Вага (кг)", blank=True, null=True)
    height = models.FloatField("Зріст (см)", blank=True, null=True)
    chest_circumference_inhale = models.FloatField("Об’єм грудної клітки (вдих)", blank=True, null=True)
    chest_circumference_exhale = models.FloatField("Об’єм грудної клітки (видих)", blank=True, null=True)
    chest_circumference_pause = models.FloatField("Об’єм грудної клітки (пауза)", blank=True, null=True)
    chest_circumference_difference = models.FloatField("Різниця об’ємів", blank=True, null=True)
    spirometry = models.FloatField("Спірометрія", blank=True, null=True)
    dynamometry_right = models.FloatField("Динамометрія (права рука)", blank=True, null=True)
    dynamometry_left = models.FloatField("Динамометрія (ліва рука)", blank=True, null=True)

    def __str__(self):
        return f"Антропометрія {self.medical_record} від {self.date_of_measurement}"


class AdditionalTests(models.Model):
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='additional_tests')
    sportsperson = models.ForeignKey(
        Sportsperson,
        on_delete=models.CASCADE,
        related_name='sportsperson_additional_tests',
        null=True,
        blank=True
    )
    ecg = models.CharField("ЕКГ", max_length=255, blank=True, null=True)
    physical_test_results = models.CharField("Результати фізичних тестів", max_length=255, blank=True, null=True)
    rufier_index = models.CharField("Проба Руф’є", max_length=100, blank=True, null=True)
    specialist_conclusion = models.CharField("Висновки спеціалістів", max_length=255, blank=True, null=True)
    ecg_file = models.BinaryField("Файл ЕКГ", blank=True, null=True)
    ecg_file_name = models.CharField("Назва файлу ЕКГ", max_length=255, blank=True, null=True)
    ecg_file_mime_type = models.CharField("MIME-тип файлу ЕКГ", max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Додаткові тести для {self.medical_record}"

class Notes(models.Model):
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='notes')
    sportsperson = models.ForeignKey(
        Sportsperson,
        on_delete=models.CASCADE,
        related_name='sportsperson_notes',
        null=True,
        blank=True
    )
    note = models.CharField("Примітка", max_length=500)
    note_file = models.BinaryField("Файл примітки", blank=True, null=True)
    note_file_name = models.CharField("Назва файлу примітки", max_length=255, blank=True, null=True)
    note_file_mime_type = models.CharField("MIME-тип файлу примітки", max_length=100, blank=True, null=True)

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