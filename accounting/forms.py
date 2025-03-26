from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget
from .models import Sportsperson, Organization, Trainer, MedicalRecord, AdditionalTests, Anthropometry, Notes


class SportspersonSearchForm(forms.Form):
    last_name = forms.CharField(label="Прізвище спортсмена", required=False)
    first_name = forms.CharField(label="Ім’я спортсмена", required=False)
    patronymic = forms.CharField(label="По батькові спортсмена", required=False)
    date_of_birth = forms.DateField(
        label="Дата народження",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    primary_sport = forms.CharField(label="Вид спорту", required=False)
    organization = forms.CharField(label="Організація", required=False)
    trainer = forms.CharField(label="Тренер", required=False)
    GENDER_CHOICES = [
        ('', '---------'),
        ('Чоловіча', 'Чоловіча'),
        ('Жіноча', 'Жіноча'),
    ]
    gender = forms.ChoiceField(
        label='Стать спортсмена',
        choices=GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class SportspersonForm(forms.ModelForm):
    trainers = forms.ModelMultipleChoiceField(
        queryset=Trainer.objects.all(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                'class': 'select2',
                'data-placeholder': 'Введіть ім’я або прізвище тренера...'  # Updated to Ukrainian
            }
        )
    )
    organizations = forms.ModelMultipleChoiceField(
        queryset=Organization.objects.all(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                'class': 'select2',
                'data-placeholder': 'Введіть назву організації...'  # Updated to Ukrainian
            }
        )
    )

    class Meta:
        model = Sportsperson
        fields = [
            'last_name', 'first_name', 'patronymic',
            'date_of_birth', 'gender', 'address', 'phone',
            'sports_category', 'primary_sport', 'additional_sports',
            'trainers', 'organizations'
        ]
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'gender': forms.Select(attrs={'class': 'form-select'}, choices=(
                ('male', 'Чоловіча'),
                ('female', 'Жіноча'),
            )),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'sports_category': forms.TextInput(attrs={'class': 'form-control'}),
            'primary_sport': forms.TextInput(attrs={'class': 'form-control'}),
            'additional_sports': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'last_name': 'Прізвище',
            'first_name': 'Ім’я',
            'patronymic': 'По батькові',
            'date_of_birth': 'Дата народження',
            'gender': 'Стать',
            'address': 'Домашня адреса',
            'phone': 'Телефон',
            'sports_category': 'Спортивний розряд',
            'primary_sport': 'Основний вид спорту',
            'additional_sports': 'Інші види спорту',
            'trainers': 'Тренери',
            'organizations': 'Організації',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure the placeholders are set correctly
        self.fields['trainers'].widget.attrs.update({
            'class': 'select2',
            'data-placeholder': 'Введіть ім’я або прізвище тренера...'
        })
        self.fields['organizations'].widget.attrs.update({
            'class': 'select2',
            'data-placeholder': 'Введіть назву організації...'
        })
        if self.instance and self.instance.pk:
            self.fields['trainers'].initial = self.instance.trainers.all()
            self.fields['organizations'].initial = self.instance.organizations.all()

    def save(self, commit=True):
        sportsperson = super().save(commit=False)
        if commit:
            sportsperson.save()
            sportsperson.trainers.set(self.cleaned_data['trainers'])
            sportsperson.organizations.set(self.cleaned_data['organizations'])
        else:
            self.save_m2m = lambda: (
                sportsperson.trainers.set(self.cleaned_data['trainers']),
                sportsperson.organizations.set(self.cleaned_data['organizations'])
            )
        return sportsperson


class TrainerForm(forms.ModelForm):
    class Meta:
        model = Trainer
        exclude = ['sportspersons']
        auto_id = "id_%s"
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'gender': forms.Select(attrs={'class': 'form-select'}, choices=(
                ('male', 'Чоловіча'),
                ('female', 'Жіноча'),
            )),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'primary_sport': forms.TextInput(attrs={'class': 'form-control'}),
            'additional_sports': forms.TextInput(attrs={'class': 'form-control'}),
            'organization': forms.SelectMultiple(attrs={
                'class': 'select2',
                'data-placeholder': 'Введіть назву організації...'
            }),
        }
        labels = {
            'last_name': 'Прізвище',
            'first_name': 'Ім’я',
            'patronymic': 'По батькові',
            'date_of_birth': 'Дата народження',
            'gender': 'Стать',
            'address': 'Домашня адреса',
            'phone': 'Телефон',
            'primary_sport': 'Основний вид спорту',
            'additional_sports': 'Інші види спорту',
            'organization': 'Організація',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure the organization field is optional
        self.fields['organization'].required = False
        # Update widget attributes for organization
        self.fields['organization'].widget.attrs.update({
            'class': 'select2',
            'data-placeholder': 'Введіть назву організації...'
        })


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        exclude = ['sportspersons']
        auto_id = "id_%s"
        widgets = {
            'organization_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'type': forms.TextInput(attrs={'class': 'form-control'}),
            'organization_document': forms.FileInput(attrs={'class': 'form-control'}),
        }


class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = '__all__'
        labels = {
            'sportsperson': 'Спортсмен',
            'date_created': 'Дата створення карти',
            'medical_facility': 'Медичний заклад',
            'health_status': 'Стан здоров’я',
            'diagnosis': 'Діагноз',
            'functional_status': 'Функціональний статус',
            'physical_activity_group': 'Група для занять',
            'admission_status': 'Допуск',
            'medical_history': 'Історія хвороб',
            'medical_document': 'Медичний документ',
        }
        widgets = {
            'sportsperson': forms.Select(attrs={
                'class': 'select2',
                'data-placeholder': 'Оберіть спортсмена...'
            }),  # Use Select with Select2 for search
            'date_created': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'medical_facility': forms.TextInput(attrs={'class': 'form-control'}),
            'health_status': forms.TextInput(attrs={'class': 'form-control'}),
            'diagnosis': forms.TextInput(attrs={'class': 'form-control'}),
            'functional_status': forms.TextInput(attrs={'class': 'form-control'}),
            'physical_activity_group': forms.TextInput(attrs={'class': 'form-control'}),
            'admission_status': forms.TextInput(attrs={'class': 'form-control'}),
            'medical_history': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medical_document': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure the sportsperson field is optional (since it's null=True in the model)
        self.fields['sportsperson'].required = False
        # Update widget attributes for sportsperson
        self.fields['sportsperson'].widget.attrs.update({
            'class': 'select2',
            'data-placeholder': 'Оберіть спортсмена...'
        })


class AnthropometryForm(forms.ModelForm):
    class Meta:
        model = Anthropometry
        fields = '__all__'
        labels = {
            'medical_record': 'Медична карта',
            'sportsperson': 'Спортсмен',
            'date_of_measurement': 'Дата вимірювання',
            'weight': 'Вага (кг)',
            'height': 'Зріст (см)',
            'chest_circumference_inhale': 'Об’єм грудної клітки (вдих)',
            'chest_circumference_exhale': 'Об’єм грудної клітки (видих)',
            'chest_circumference_pause': 'Об’єм грудної клітки (пауза)',
            'chest_circumference_difference': 'Різниця об’ємів',
            'spirometry': 'Спірометрія',
            'dynamometry_right': 'Динамометрія (права)',
            'dynamometry_left': 'Динамометрія (ліва)',
        }
        widgets = {
            'medical_record': forms.Select(attrs={'class': 'form-select'}),
            'sportsperson': forms.Select(attrs={'class': 'form-select'}),
            'date_of_measurement': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'height': forms.NumberInput(attrs={'class': 'form-control'}),
            'chest_circumference_inhale': forms.NumberInput(attrs={'class': 'form-control'}),
            'chest_circumference_exhale': forms.NumberInput(attrs={'class': 'form-control'}),
            'chest_circumference_pause': forms.NumberInput(attrs={'class': 'form-control'}),
            'chest_circumference_difference': forms.NumberInput(attrs={'class': 'form-control'}),
            'spirometry': forms.NumberInput(attrs={'class': 'form-control'}),
            'dynamometry_right': forms.NumberInput(attrs={'class': 'form-control'}),
            'dynamometry_left': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, sportsperson=None, medical_record=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['medical_record'].required = True
        self.fields['sportsperson'].required = False
        self.fields['sportsperson'].widget.attrs['readonly'] = True
        # Predefine and make medical_record read-only if provided
        if medical_record:
            self.fields['medical_record'].queryset = MedicalRecord.objects.filter(pk=medical_record.pk)
            self.fields['medical_record'].initial = medical_record
            self.fields['medical_record'].widget.attrs['readonly'] = True
        # Filter medical records by sportsperson if provided
        if sportsperson:
            self.fields['medical_record'].queryset = MedicalRecord.objects.filter(sportsperson=sportsperson)
            self.fields['sportsperson'].queryset = Sportsperson.objects.filter(pk=sportsperson.pk)
            self.fields['sportsperson'].initial = sportsperson


class AdditionalTestsForm(forms.ModelForm):
    class Meta:
        model = AdditionalTests
        fields = '__all__'
        labels = {
            'medical_record': 'Медична карта',
            'sportsperson': 'Спортсмен',
            'ecg': 'ЕКГ',
            'physical_test_results': 'Результати фізичних тестів',
            'rufier_index': 'Проба Руф’є',
            'specialist_conclusion': 'Висновки спеціалістів',
            'ecg_file': 'Файл ЕКГ',
        }
        widgets = {
            'medical_record': forms.Select(attrs={'class': 'form-select'}),
            'sportsperson': forms.Select(attrs={'class': 'form-select'}),
            'ecg': forms.TextInput(attrs={'class': 'form-control'}),
            'physical_test_results': forms.TextInput(attrs={'class': 'form-control'}),
            'rufier_index': forms.TextInput(attrs={'class': 'form-control'}),
            'specialist_conclusion': forms.TextInput(attrs={'class': 'form-control'}),
            'ecg_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, sportsperson=None, medical_record=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['medical_record'].required = True
        self.fields['sportsperson'].required = False
        self.fields['sportsperson'].widget.attrs['readonly'] = True
        # Predefine and make medical_record read-only if provided
        if medical_record:
            self.fields['medical_record'].queryset = MedicalRecord.objects.filter(pk=medical_record.pk)
            self.fields['medical_record'].initial = medical_record
            self.fields['medical_record'].widget.attrs['readonly'] = True
        # Filter medical records by sportsperson if provided
        if sportsperson:
            self.fields['medical_record'].queryset = MedicalRecord.objects.filter(sportsperson=sportsperson)
            self.fields['sportsperson'].queryset = Sportsperson.objects.filter(pk=sportsperson.pk)
            self.fields['sportsperson'].initial = sportsperson


class NotesForm(forms.ModelForm):
    class Meta:
        model = Notes
        fields = '__all__'
        labels = {
            'medical_record': 'Медична карта',
            'sportsperson': 'Спортсмен',
            'note': 'Примітка',
            'note_file': 'Файл примітки',
        }
        widgets = {
            'medical_record': forms.Select(attrs={'class': 'form-select'}),
            'sportsperson': forms.Select(attrs={'class': 'form-select'}),
            'note': forms.TextInput(attrs={'class': 'form-control'}),
            'note_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, sportsperson=None, medical_record=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['medical_record'].required = True
        self.fields['sportsperson'].required = False
        self.fields['sportsperson'].widget.attrs['readonly'] = True
        # Predefine and make medical_record read-only if provided
        if medical_record:
            self.fields['medical_record'].queryset = MedicalRecord.objects.filter(pk=medical_record.pk)
            self.fields['medical_record'].initial = medical_record
            self.fields['medical_record'].widget.attrs['readonly'] = True
        # Filter medical records by sportsperson if provided
        if sportsperson:
            self.fields['medical_record'].queryset = MedicalRecord.objects.filter(sportsperson=sportsperson)
            self.fields['sportsperson'].queryset = Sportsperson.objects.filter(pk=sportsperson.pk)
            self.fields['sportsperson'].initial = sportsperson
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")