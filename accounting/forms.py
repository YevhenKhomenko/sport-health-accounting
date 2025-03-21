from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django_select2.forms import ModelSelect2Widget
from .models import Sportsperson, Organization, Trainer, MedicalRecord, AdditionalTests, Anthropometry


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
    organization = forms.ModelChoiceField(
        label="Організація",
        queryset=Organization.objects.all(),
        required=False
    )
    trainer = forms.ModelChoiceField(
        label="Тренер",
        queryset=Trainer.objects.all(),
        required=False
    )
    gender = forms.ChoiceField(
        label="Стать спортсмена",
        choices=[('', '---------'), ('male', 'Чоловіча'), ('female', 'Жіноча')],
        required=False
    )


class SportspersonForm(forms.ModelForm):
    class Meta:
        model = Sportsperson
        exclude = ['trainers', 'organizations', 'medical_records', 'anthropometries', 'notes']
        auto_id = 'id_%s'
        widgets = {
            'date_of_birth': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'gender': forms.Select(attrs={'class': 'form-select'}, choices=(
                ('male', 'Чоловіча'),
                ('female', 'Жіноча'),
            )),
        }


class TrainerForm(forms.ModelForm):
    class Meta:
        model = Trainer
        exclude = ['sportspersons']
        auto_id = "id_%s"
        widgets = {
            'date_of_birth': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
            'gender': forms.Select(
                attrs={'class': 'form-select'},
                choices=[('male', 'Чоловіча'), ('female', 'Жіноча')]
            ),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'primary_sport': forms.TextInput(attrs={'class': 'form-control'}),
            'additional_sports': forms.TextInput(attrs={'class': 'form-control'}),
        }


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
        }
        widgets = {
          #  'sportsperson': ModelSelect2Widget(
          #      model=Sportsperson,
          #      search_fields=['last_name__icontains', 'first_name__icontains'],
          #      attrs={'data-placeholder': 'Оберіть спортсмена...'}
          #  ),
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


class AdditionalTestsForm(forms.ModelForm):
    class Meta:
        model = AdditionalTests
        fields = '__all__'
        auto_id = "id_%s"
        widgets = {
            'ecg': forms.TextInput(attrs={'class': 'form-control'}),
            'physical_test_results': forms.TextInput(attrs={'class': 'form-control'}),
            'rufier_index': forms.TextInput(attrs={'class': 'form-control'}),
            'specialist_conclusion': forms.TextInput(attrs={'class': 'form-control'}),
            'ecg_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class AnthropometryForm(forms.ModelForm):
    class Meta:
        model = Anthropometry
        fields = '__all__'
        auto_id = "id_%s"
        widgets = {
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


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")