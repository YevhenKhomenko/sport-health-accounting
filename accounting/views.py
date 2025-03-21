from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.utils.decorators import method_decorator
from .models import (
    Sportsperson, Trainer, Organization, MedicalRecord,
    Anthropometry, AdditionalTests, Notes, UserProfile
)
from .forms import SportspersonSearchForm, SportspersonForm, TrainerForm, OrganizationForm, AnthropometryForm, \
    AdditionalTestsForm, MedicalRecordForm, RegistrationForm
from .permissions import role_required

# TODO: add register view(login pass, then admin approve)


class NextUrlMixin:
    def get_success_url(self):
        next_url = self.request.GET.get('next') or self.request.POST.get('next')
        if next_url:
            return next_url
        return super().get_success_url()


def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # користувач може бути активним, але профіль з "pending" за замовчуванням
            user.save()
            # Створення профілю з роллю "pending"
            UserProfile.objects.create(user=user, role='pending')
            messages.info(request, "Ваш запит на реєстрацію направлено на розгляд. Будь ласка, зачекайте схвалення.")
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'accounting/registration.html', {'form': form})


def login_view(request):
    from django.contrib.auth import authenticate, login
    from django.contrib import messages
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            # Перевірка статусу реєстрації
            if hasattr(user, 'userprofile') and user.userprofile.role == 'pending':
                messages.error(request, "Ваш запит на реєстрацію знаходиться на розгляді. Спробуйте пізніше.")
                return redirect('login')
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Невірний логін або пароль")
    return render(request, 'accounting/login.html')


def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    # Стартова сторінка
    form = SportspersonSearchForm(request.GET or None)
    context = {'form': form}
    return render(request, 'accounting/dashboard.html', context)


@login_required
def sportsperson_list(request):
    form = SportspersonSearchForm(request.GET or None)
    queryset = Sportsperson.objects.all()

    year_of_birth = request.GET.get('year_of_birth')

    if form.is_valid():
        if form.cleaned_data.get('last_name'):
            queryset = queryset.filter(last_name__icontains=form.cleaned_data['last_name'])
        if form.cleaned_data.get('first_name'):
            queryset = queryset.filter(first_name__icontains=form.cleaned_data['first_name'])
        if form.cleaned_data.get('patronymic'):
            queryset = queryset.filter(patronymic__icontains=form.cleaned_data['patronymic'])
        if year_of_birth:
            try:
                year = int(year_of_birth)
                queryset = queryset.filter(date_of_birth__year=year)
            except ValueError:
                pass
        if form.cleaned_data.get('primary_sport'):
            queryset = queryset.filter(primary_sport__icontains=form.cleaned_data['primary_sport'])
        if request.GET.get('organization'):
            queryset = queryset.filter(organizations__organization_name__icontains=request.GET.get('organization'))
        if request.GET.get('trainer'):
            queryset = queryset.filter(trainers__last_name__icontains=request.GET.get('trainer'))
        if form.cleaned_data.get('gender'):
            queryset = queryset.filter(gender=form.cleaned_data['gender'])
    context = {'form': form, 'sportsperson_list': queryset.distinct()}
    return render(request, 'accounting/sportperson_list.html', context)


@login_required
def sportsperson_detail(request, pk):
    sportsperson = get_object_or_404(Sportsperson, pk=pk)
    # Отримуємо пов'язані об’єкти
    trainers = sportsperson.trainers.all()
    organizations = sportsperson.organizations.all()
    medical_records = sportsperson.medical_records.all().order_by('-date_created')
    # Для антропометрії та нотаток – через медичні записи
    from accounting.models import Anthropometry, Notes
    anthropometries = Anthropometry.objects.filter(medical_record__sportsperson=sportsperson).order_by('-date_of_measurement')
    notes = Notes.objects.filter(medical_record__sportsperson=sportsperson).order_by('-id')
    context = {
        'sportsperson': sportsperson,
        'trainers': trainers,
        'organizations': organizations,
        'medical_records': medical_records,
        'anthropometries': anthropometries,
        'notes': notes,
    }
    return render(request, 'accounting/sportperson_detail.html', context)



@login_required
def organization_detail(request, pk):
    organization = get_object_or_404(Organization, pk=pk)
    sportspeople = Sportsperson.objects.filter(organizations=organization)
    context = {'organization': organization, 'sportspeople': sportspeople}
    return render(request, 'accounting/organization_detail.html', context)


@login_required
def trainer_detail(request, pk):
    trainer = get_object_or_404(Trainer, pk=pk)
    sportspeople = Sportsperson.objects.filter(trainers=trainer)
    context = {'trainer': trainer, 'sportspeople': sportspeople}
    return render(request, 'accounting/trainer_detail.html', context)


@login_required
def medicalrecord_detail(request, pk):
    medicalrecord = get_object_or_404(MedicalRecord, pk=pk)
    context = {'medicalrecord': medicalrecord}
    return render(request, 'accounting/medicalrecord_detail.html', context)


@login_required
def additionaltests_detail(request, pk):
    additionaltest = get_object_or_404(AdditionalTests, pk=pk)
    context = {'additionaltests': additionaltest}
    return render(request, 'accounting/additionaltests_detail.html', context)


@login_required
def note_detail(request, pk):
    note = get_object_or_404(Notes, pk=pk)
    context = {'note': note}
    return render(request, 'accounting/notes_detail.html', context)


@login_required
def anthropometry_detail(request, pk):
    anthropometry = get_object_or_404(Anthropometry, pk=pk)
    context = {'anthropometry': anthropometry}
    return render(request, 'accounting/anthropometry_detail.html', context)


# --- CRUD для Sportsperson ---
@method_decorator(role_required(['admin', 'editor']), name='dispatch')
class SportspersonCreateView(CreateView):
    model = Sportsperson
    fields = '__all__'
    template_name = 'accounting/sportperson_create.html'
    success_url = reverse_lazy('sportsperson_list')


@method_decorator(role_required(['admin']), name='dispatch')
class SportspersonUpdateView(UpdateView):
    model = Sportsperson
    form_class = SportspersonForm
    template_name = 'accounting/sportperson_form.html'
    success_url = reverse_lazy('sportsperson_list')

    def form_valid(self, form):
        print("Form is valid. Cleaned data:", form.cleaned_data)
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Form errors:", form.errors)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sportsperson'] = self.object
        context['trainers'] = self.object.trainers.all()
        context['organizations'] = self.object.organizations.all()
        context['medical_records'] = self.object.medical_records.all().order_by('-date_created')
        from accounting.models import Anthropometry, Notes
        context['anthropometries'] = Anthropometry.objects.filter(medical_record__sportsperson=self.object).order_by('-date_of_measurement')
        context['notes'] = Notes.objects.filter(medical_record__sportsperson=self.object)
        return context


@method_decorator(role_required(['admin']), name='dispatch')
class SportspersonDeleteView(DeleteView):
    model = Sportsperson
    template_name = 'accounting/sportperson_confirm_delete.html'
    success_url = reverse_lazy('sportsperson_list')


# --- CRUD для Trainer ---
class TrainerListView(ListView):
    model = Trainer
    template_name = 'accounting/trainer_list.html'
    context_object_name = 'trainer_list'

    def get_queryset(self):
        qs = super().get_queryset()
        last_name = self.request.GET.get('last_name')
        first_name = self.request.GET.get('first_name')
        if last_name:
            qs = qs.filter(last_name__icontains=last_name)
        if first_name:
            qs = qs.filter(first_name__icontains=first_name)
        return qs


@method_decorator(role_required(['admin', 'editor']), name='dispatch')
class TrainerCreateView(CreateView):
    model = Trainer
    fields = '__all__'
    template_name = 'accounting/trainer_create.html'
    success_url = reverse_lazy('trainer_list')


@method_decorator(role_required(['admin']), name='dispatch')
class TrainerUpdateView(UpdateView):
    model = Trainer
    form_class = TrainerForm
    template_name = 'accounting/trainer_form.html'
    success_url = reverse_lazy('trainer_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trainer'] = self.object
        context['sportspersons'] = Sportsperson.objects.filter(trainers=self.object)
        return context


@method_decorator(role_required(['admin']), name='dispatch')
class TrainerDeleteView(DeleteView):
    model = Trainer
    template_name = 'accounting/trainer_confirm_delete.html'
    success_url = reverse_lazy('trainer_list')


# --- CRUD для Organization ---
class OrganizationListView(ListView):
    model = Organization
    template_name = 'accounting/organization_list.html'
    context_object_name = 'organization_list'

    def get_queryset(self):
        qs = super().get_queryset()
        name = self.request.GET.get('name')
        if name:
            qs = qs.filter(organization_name__icontains=name)
        return qs


@method_decorator(role_required(['admin', 'editor']), name='dispatch')
class OrganizationCreateView(CreateView):
    model = Organization
    fields = '__all__'
    template_name = 'accounting/organization_create.html'
    success_url = reverse_lazy('organization_list')


@method_decorator(role_required(['admin']), name='dispatch')
class OrganizationUpdateView(UpdateView):
    model = Organization
    form_class = OrganizationForm
    template_name = 'accounting/organization_form.html'
    success_url = reverse_lazy('organization_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization'] = self.object
        # Отримуємо спортсменів, пов'язаних з цією організацією
        from accounting.models import Sportsperson
        context['sportspersons'] = Sportsperson.objects.filter(organizations=self.object)
        return context


@method_decorator(role_required(['admin']), name='dispatch')
class OrganizationDeleteView(DeleteView):
    model = Organization
    template_name = 'accounting/organization_confirm_delete.html'
    success_url = reverse_lazy('organization_list')


# --- CRUD для MedicalRecord ---
class MedicalRecordListView(ListView):
    model = MedicalRecord
    template_name = 'accounting/medicalrecord_list.html'
    context_object_name = 'medicalrecord_list'


@method_decorator(role_required(['admin', 'editor']), name='dispatch')
class MedicalRecordCreateGlobalView(NextUrlMixin, CreateView):
    model = MedicalRecord
    form_class = MedicalRecordForm
    template_name = 'accounting/medicalrecord_create.html'
    success_url = reverse_lazy('medicalrecord_list')


@method_decorator(role_required(['admin', 'editor']), name='dispatch')
class MedicalRecordCreateView(NextUrlMixin, CreateView):
    model = MedicalRecord
    form_class = MedicalRecordForm
    template_name = 'accounting/medicalrecord_create.html'
    success_url = reverse_lazy('sportsperson_list')

    def get_initial(self):
        initial = super().get_initial()
        sportsperson_id = self.kwargs.get('sportsperson_id')
        if sportsperson_id:
            initial['sportsperson'] = sportsperson_id
        return initial


@method_decorator(role_required(['admin']), name='dispatch')
class MedicalRecordUpdateView(UpdateView):
    model = MedicalRecord
    form_class = MedicalRecordForm
    template_name = 'accounting/medicalrecord_form.html'
    success_url = reverse_lazy('sportsperson_list')


@method_decorator(role_required(['admin']), name='dispatch')
class MedicalRecordDeleteView(DeleteView):
    model = MedicalRecord
    template_name = 'accounting/medicalrecord_confirm_delete.html'
    success_url = reverse_lazy('sportsperson_list')

@login_required
def medicalrecord_select_unassigned(request):
    sportsperson_id = request.GET.get('sportsperson_id')
    # Фільтруємо записи, у яких sportsperson не визначено (null)
    unassigned_records = MedicalRecord.objects.filter(sportsperson__isnull=True)
    context = {
        'unassigned_records': unassigned_records,
        'sportsperson_id': sportsperson_id,
    }
    return render(request, 'accounting/medicalrecord_select_unassigned.html', context)


@login_required
def assign_medicalrecord(request, record_pk):
    sportsperson_id = request.GET.get('sportsperson_id')
    record = get_object_or_404(MedicalRecord, pk=record_pk)
    sportsperson = get_object_or_404(Sportsperson, pk=sportsperson_id)
    record.sportsperson = sportsperson
    record.save()
    # Після призначення перенаправляємо на детальну сторінку спортсмена
    return redirect('sportsperson_detail', pk=sportsperson.pk)


# --- CRUD для Anthropometry ---
class AnthropometryListView(ListView):
    model = Anthropometry
    template_name = 'accounting/anthropometry_list.html'
    context_object_name = 'anthropometry_list'


@method_decorator(role_required(['admin', 'editor']), name='dispatch')
class AnthropometryCreateView(CreateView):
    model = Anthropometry
    fields = '__all__'
    template_name = 'accounting/anthropometry_create.html'
    success_url = reverse_lazy('anthropometry_list')


@method_decorator(role_required(['admin']), name='dispatch')
class AnthropometryUpdateView(UpdateView):
    model = Anthropometry
    form_class = AnthropometryForm
    template_name = 'accounting/anthropometry_form.html'
    success_url = reverse_lazy('anthropometry_list')


@method_decorator(role_required(['admin']), name='dispatch')
class AnthropometryDeleteView(DeleteView):
    model = Anthropometry
    template_name = 'accounting/anthropometry_confirm_delete.html'
    success_url = reverse_lazy('anthropometry_list')


# --- CRUD для AdditionalTests ---
class AdditionalTestsListView(ListView):
    model = AdditionalTests
    template_name = 'accounting/additionaltests_list.html'
    context_object_name = 'additionaltests_list'


@method_decorator(role_required(['admin', 'editor']), name='dispatch')
class AdditionalTestsCreateView(CreateView):
    model = AdditionalTests
    fields = '__all__'
    template_name = 'accounting/additionaltests_create.html'
    success_url = reverse_lazy('additionaltests_list')

    def get_initial(self):
        initial = super().get_initial()
        record_id = self.kwargs.get('record_id')
        if record_id:
            initial['medical_record'] = record_id
        return initial


@method_decorator(role_required(['admin', 'editor']), name='dispatch')
class AdditionalTestsCreateGlobalView(CreateView):
    model = AdditionalTests
    fields = '__all__'
    template_name = 'accounting/additionaltests_form.html'
    success_url = reverse_lazy('additionaltests_list')


@method_decorator(role_required(['admin']), name='dispatch')
class AdditionalTestsUpdateView(UpdateView):
    model = AdditionalTests
    form_class = AdditionalTestsForm
    template_name = 'accounting/additionaltests_form.html'
    success_url = reverse_lazy('additionaltests_list')


@method_decorator(role_required(['admin']), name='dispatch')
class AdditionalTestsDeleteView(DeleteView):
    model = AdditionalTests
    template_name = 'accounting/additionaltests_confirm_delete.html'
    success_url = reverse_lazy('additionaltests_list')


# --- CRUD для Notes ---
class NotesListView(ListView):
    model = Notes
    template_name = 'accounting/notes_list.html'
    context_object_name = 'notes_list'


@method_decorator(role_required(['admin', 'editor']), name='dispatch')
class NotesCreateView(CreateView):
    model = Notes
    fields = '__all__'
    template_name = 'accounting/notes_create.html'
    success_url = reverse_lazy('notes_list')

    def get_initial(self):
        initial = super().get_initial()
        record_id = self.kwargs.get('record_id')
        if record_id:
            initial['medical_record'] = record_id
        return initial


@method_decorator(role_required(['admin', 'editor']), name='dispatch')
class NotesCreateGlobalView(CreateView):
    model = Notes
    fields = '__all__'
    template_name = 'accounting/notes_form.html'
    success_url = reverse_lazy('notes_list')


@method_decorator(role_required(['admin']), name='dispatch')
class NotesUpdateView(UpdateView):
    model = Notes
    fields = '__all__'
    template_name = 'accounting/notes_form.html'
    success_url = reverse_lazy('notes_list')


@method_decorator(role_required(['admin']), name='dispatch')
class NotesDeleteView(DeleteView):
    model = Notes
    template_name = 'accounting/notes_confirm_delete.html'
    success_url = reverse_lazy('notes_list')
