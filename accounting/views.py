from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.utils.decorators import method_decorator
from .models import (
    Sportsperson, Trainer, Organization, MedicalRecord,
    Anthropometry, AdditionalTests, Notes, UserProfile
)
from .forms import SportspersonSearchForm, SportspersonForm, TrainerForm, OrganizationForm, AnthropometryForm, \
    AdditionalTestsForm, MedicalRecordForm, RegistrationForm, NotesForm
from .permissions import role_required


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

    if form.is_valid():
        if form.cleaned_data.get('last_name'):
            queryset = queryset.filter(last_name__icontains=form.cleaned_data['last_name'])
        if form.cleaned_data.get('first_name'):
            queryset = queryset.filter(first_name__icontains=form.cleaned_data['first_name'])
        if form.cleaned_data.get('patronymic'):
            queryset = queryset.filter(patronymic__icontains=form.cleaned_data['patronymic'])
        if form.cleaned_data.get('date_of_birth'):
            queryset = queryset.filter(date_of_birth=form.cleaned_data['date_of_birth'])
        if form.cleaned_data.get('primary_sport'):
            queryset = queryset.filter(primary_sport__icontains=form.cleaned_data['primary_sport'])
        if form.cleaned_data.get('organization'):
            queryset = queryset.filter(organizations__organization_name__icontains=form.cleaned_data['organization'])
        if form.cleaned_data.get('trainer'):
            queryset = queryset.filter(trainers__last_name__icontains=form.cleaned_data['trainer'])
        if form.cleaned_data.get('gender'):
            queryset = queryset.filter(gender=form.cleaned_data['gender'])

    paginator = Paginator(queryset.distinct(), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'sportsperson_list': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'accounting/sportperson_list.html', context)


@login_required
def sportsperson_detail(request, pk):
    sportsperson = get_object_or_404(Sportsperson, pk=pk)
    # Отримуємо пов'язані об’єкти
    trainers = sportsperson.trainers.all()
    organizations = sportsperson.organizations.all()
    medical_records = sportsperson.medical_records.all().order_by('-date_created')
    # Для антропометрії, нотаток та додаткових тестів – через медичні записи
    from accounting.models import Anthropometry, Notes, Trainer, Organization, AdditionalTests
    anthropometries = Anthropometry.objects.filter(medical_record__sportsperson=sportsperson).order_by('-date_of_measurement')
    notes = Notes.objects.filter(medical_record__sportsperson=sportsperson).order_by('-id')
    additional_tests = AdditionalTests.objects.filter(medical_record__sportsperson=sportsperson)
    # Отримуємо всіх тренерів та організації для форм додавання
    all_trainers = Trainer.objects.all()
    all_organizations = Organization.objects.all()
    context = {
        'sportsperson': sportsperson,
        'trainers': trainers,
        'organizations': organizations,
        'medical_records': medical_records,
        'anthropometries': anthropometries,
        'notes': notes,
        'additional_tests': additional_tests,
        'all_trainers': all_trainers,
        'all_organizations': all_organizations,
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
    # Fetch related objects
    anthropometries = medicalrecord.anthropometries.all().order_by('-date_of_measurement')
    additional_tests = medicalrecord.additional_tests.all()
    notes = medicalrecord.notes.all().order_by('-id')
    context = {
        'medicalrecord': medicalrecord,
        'anthropometries': anthropometries,
        'additional_tests': additional_tests,
        'notes': notes,
    }
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
    form_class = SportspersonForm
    template_name = 'accounting/sportperson_create.html'

    def get_success_url(self):
        # Після успішного створення повертаємо URL для сторінки деталей спортсмена
        return reverse_lazy('sportsperson_detail', kwargs={'pk': self.object.pk})


@method_decorator(role_required(['admin']), name='dispatch')
class SportspersonUpdateView(UpdateView):
    model = Sportsperson
    form_class = SportspersonForm
    template_name = 'accounting/sportperson_form.html'

    def get_success_url(self):
        # Повертаємо URL для деталей спортсмена за допомогою його pk
        return reverse_lazy('sportsperson_detail', kwargs={'pk': self.object.pk})

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


@method_decorator(role_required(['admin', 'editor']), name='dispatch')
class SportspersonAddTrainerView(View):
    def post(self, request, sportsperson_pk):
        sportsperson = get_object_or_404(Sportsperson, pk=sportsperson_pk)
        trainer_pk = request.POST.get('trainer')
        trainer = get_object_or_404(Trainer, pk=trainer_pk)
        sportsperson.trainers.add(trainer)
        messages.success(request, f"Тренера {trainer} успішно додано до спортсмена {sportsperson}.")
        return redirect('sportsperson_detail', pk=sportsperson.pk)


@method_decorator(role_required(['admin', 'editor']), name='dispatch')
class SportspersonRemoveTrainerView(View):
    def post(self, request, sportsperson_pk, trainer_pk):
        sportsperson = get_object_or_404(Sportsperson, pk=sportsperson_pk)
        trainer = get_object_or_404(Trainer, pk=trainer_pk)
        sportsperson.trainers.remove(trainer)
        messages.success(request, f"Тренера {trainer} успішно видалено зі списку спортсмена {sportsperson}.")
        return redirect('sportsperson_detail', pk=sportsperson.pk)


@method_decorator(role_required(['admin', 'editor']), name='dispatch')
class SportspersonAddOrganizationView(View):
    def post(self, request, sportsperson_pk):
        sportsperson = get_object_or_404(Sportsperson, pk=sportsperson_pk)
        organization_pk = request.POST.get('organization')
        organization = get_object_or_404(Organization, pk=organization_pk)
        sportsperson.organizations.add(organization)
        messages.success(request, f"Організацію {organization} успішно додано до спортсмена {sportsperson}.")
        return redirect('sportsperson_detail', pk=sportsperson.pk)


@method_decorator(role_required(['admin', 'editor']), name='dispatch')
class SportspersonRemoveOrganizationView(View):
    def post(self, request, sportsperson_pk, organization_pk):
        sportsperson = get_object_or_404(Sportsperson, pk=sportsperson_pk)
        organization = get_object_or_404(Organization, pk=organization_pk)
        sportsperson.organizations.remove(organization)
        messages.success(request, f"Організацію {organization} успішно видалено зі списку спортсмена {sportsperson}.")
        return redirect('sportsperson_detail', pk=sportsperson.pk)


@method_decorator(role_required(['admin']), name='dispatch')
class SportspersonDeleteView(DeleteView):
    model = Sportsperson
    template_name = 'accounting/sportperson_confirm_delete.html'
    success_url = reverse_lazy('sportperson_list')


# --- CRUD для Trainer ---
class TrainerListView(ListView):
    model = Trainer
    template_name = 'accounting/trainer_list.html'
    context_object_name = 'trainer_list'
    paginate_by = 10  # 10 items per page

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
    form_class = TrainerForm
    template_name = 'accounting/trainer_create.html'

    def get_success_url(self):
        # Redirect to the created trainer's detail page
        return reverse_lazy('trainer_detail', kwargs={'pk': self.object.pk})


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

    def get_success_url(self):
        return reverse_lazy('trainer_detail', kwargs={'pk': self.object.pk})


@method_decorator(role_required(['admin']), name='dispatch')
class TrainerDeleteView(DeleteView):
    model = Trainer
    template_name = 'accounting/trainer_confirm_delete.html'
    success_url = reverse_lazy('dashboard')


# --- CRUD для Organization ---
class OrganizationListView(ListView):
    model = Organization
    template_name = 'accounting/organization_list.html'
    context_object_name = 'organization_list'
    paginate_by = 10  # 10 items per page

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

    def get_success_url(self):
        return reverse_lazy('organization_detail', kwargs={'pk': self.object.pk})


@method_decorator(role_required(['admin']), name='dispatch')
class OrganizationUpdateView(UpdateView):
    model = Organization
    form_class = OrganizationForm
    template_name = 'accounting/organization_form.html'

    def get_success_url(self):
        return reverse_lazy('organization_detail', kwargs={'pk': self.object.pk})

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
    success_url = reverse_lazy('dashboard')


# --- CRUD для MedicalRecord ---
class MedicalRecordListView(ListView):
    model = MedicalRecord
    template_name = 'accounting/medicalrecord_list.html'
    context_object_name = 'medicalrecord_list'
    paginate_by = 10  # 10 items per page


@method_decorator(role_required(['admin', 'editor']), name='dispatch')
class MedicalRecordCreateGlobalView(CreateView):
    model = MedicalRecord
    form_class = MedicalRecordForm
    template_name = 'accounting/medicalrecord_create.html'

    def get_success_url(self):
        return reverse_lazy('medicalrecord_detail', kwargs={'pk': self.object.pk})


@method_decorator(role_required(['admin', 'editor']), name='dispatch')
class MedicalRecordCreateView(NextUrlMixin, CreateView):
    model = MedicalRecord
    form_class = MedicalRecordForm
    template_name = 'accounting/medicalrecord_create.html'

    def get_success_url(self):
        return reverse_lazy('medicalrecord_detail', kwargs={'pk': self.object.pk})

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

    def get_success_url(self):
        return reverse_lazy('medicalrecord_detail', kwargs={'pk': self.object.pk})


@method_decorator(role_required(['admin']), name='dispatch')
class MedicalRecordDeleteView(DeleteView):
    model = MedicalRecord
    template_name = 'accounting/medicalrecord_confirm_delete.html'
    success_url = reverse_lazy('dashboard')

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
    paginate_by = 10  # 10 items per page


@method_decorator(role_required(['admin', 'editor']), name='dispatch')
class AnthropometryCreateView(NextUrlMixin, CreateView):
    model = Anthropometry
    form_class = AnthropometryForm
    template_name = 'accounting/anthropometry_create.html'

    def get_initial(self):
        initial = super().get_initial()
        sportsperson_id = self.kwargs.get('sportsperson_id') or self.request.GET.get('sportsperson_id')
        if sportsperson_id:
            sportsperson = get_object_or_404(Sportsperson, pk=sportsperson_id)
            initial['sportsperson'] = sportsperson
        record_id = self.request.GET.get('record_id') or self.kwargs.get('record_id')
        if record_id:
            medical_record = get_object_or_404(MedicalRecord, pk=record_id)
            initial['medical_record'] = medical_record
            initial['sportsperson'] = medical_record.sportsperson
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        sportsperson_id = self.kwargs.get('sportsperson_id') or self.request.GET.get('sportsperson_id')
        record_id = self.request.GET.get('record_id') or self.kwargs.get('record_id')
        if sportsperson_id:
            sportsperson = get_object_or_404(Sportsperson, pk=sportsperson_id)
            kwargs['sportsperson'] = sportsperson
        if record_id:
            medical_record = get_object_or_404(MedicalRecord, pk=record_id)
            kwargs['medical_record'] = medical_record
        return kwargs

    def form_valid(self, form):
        anthropometry = form.save(commit=False)
        if form.cleaned_data['medical_record']:
            anthropometry.sportsperson = form.cleaned_data['medical_record'].sportsperson
        anthropometry.save()
        return super().form_valid(form)

    def get_success_url(self):
        # Use NextUrlMixin to handle the 'next' parameter
        next_url = super().get_success_url()
        if next_url:
            if 'medicalrecord' in next_url:
                return next_url  # Redirect to MedicalRecord detail if 'next' points there
            elif 'sportsperson' in next_url:
                return next_url  # Redirect to Sportsperson detail if 'next' points there
        # Default redirect to the associated MedicalRecord detail page
        return reverse_lazy('medicalrecord_detail', kwargs={'pk': self.object.medical_record.pk})


@method_decorator(role_required(['admin']), name='dispatch')
class AnthropometryUpdateView(UpdateView):
    model = Anthropometry
    form_class = AnthropometryForm
    template_name = 'accounting/anthropometry_form.html'

    def get_success_url(self):
        # Check for 'next' parameter
        next_url = self.request.GET.get('next') or self.request.POST.get('next')
        if next_url:
            if 'medicalrecord' in next_url:
                return next_url  # Redirect to MedicalRecord detail if 'next' points there
            elif 'sportsperson' in next_url:
                return next_url  # Redirect to Sportsperson detail if 'next' points there
        # Default redirect to the associated MedicalRecord detail page
        return reverse_lazy('medicalrecord_detail', kwargs={'pk': self.object.medical_record.pk})


@method_decorator(role_required(['admin']), name='dispatch')
class AnthropometryDeleteView(DeleteView):
    model = Anthropometry
    template_name = 'accounting/anthropometry_confirm_delete.html'

    def get_success_url(self):
        # Store the medical_record.pk before deletion
        medical_record_pk = self.object.medical_record.pk
        # Check for 'next' parameter
        next_url = self.request.GET.get('next') or self.request.POST.get('next')
        if next_url:
            if 'medicalrecord' in next_url:
                return next_url  # Redirect to MedicalRecord detail if 'next' points there
            elif 'sportsperson' in next_url:
                return next_url  # Redirect to Sportsperson detail if 'next' points there
        # Default redirect to the associated MedicalRecord detail page
        return reverse_lazy('medicalrecord_detail', kwargs={'pk': medical_record_pk})


# --- CRUD для AdditionalTests ---
class AdditionalTestsListView(ListView):
    model = AdditionalTests
    template_name = 'accounting/additionaltests_list.html'
    context_object_name = 'additionaltests_list'
    paginate_by = 10  # 10 items per page


@method_decorator(role_required(['admin', 'editor']), name='dispatch')
class AdditionalTestsCreateView(NextUrlMixin, CreateView):
    model = AdditionalTests
    form_class = AdditionalTestsForm
    template_name = 'accounting/additionaltests_create.html'

    def get_initial(self):
        initial = super().get_initial()
        sportsperson_id = self.kwargs.get('sportsperson_id') or self.request.GET.get('sportsperson_id')
        if sportsperson_id:
            sportsperson = get_object_or_404(Sportsperson, pk=sportsperson_id)
            initial['sportsperson'] = sportsperson
        record_id = self.kwargs.get('record_id') or self.request.GET.get('record_id')
        if record_id:
            medical_record = get_object_or_404(MedicalRecord, pk=record_id)
            initial['medical_record'] = medical_record
            initial['sportsperson'] = medical_record.sportsperson
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        sportsperson_id = self.kwargs.get('sportsperson_id') or self.request.GET.get('sportsperson_id')
        record_id = self.kwargs.get('record_id') or self.request.GET.get('record_id')
        if sportsperson_id:
            sportsperson = get_object_or_404(Sportsperson, pk=sportsperson_id)
            kwargs['sportsperson'] = sportsperson
        if record_id:
            medical_record = get_object_or_404(MedicalRecord, pk=record_id)
            kwargs['medical_record'] = medical_record
        return kwargs

    def form_valid(self, form):
        additional_test = form.save(commit=False)
        if form.cleaned_data['medical_record']:
            additional_test.sportsperson = form.cleaned_data['medical_record'].sportsperson
        additional_test.save()
        return super().form_valid(form)

    def get_success_url(self):
        # Use NextUrlMixin to handle the 'next' parameter
        next_url = super().get_success_url()
        if next_url:
            if 'medicalrecord' in next_url:
                return next_url  # Redirect to MedicalRecord detail if 'next' points there
            elif 'sportsperson' in next_url:
                return next_url  # Redirect to Sportsperson detail if 'next' points there
        # Default redirect to the associated MedicalRecord detail page
        return reverse_lazy('medicalrecord_detail', kwargs={'pk': self.object.medical_record.pk})


@method_decorator(role_required(['admin', 'editor']), name='dispatch')
class AdditionalTestsCreateGlobalView(CreateView):
    model = AdditionalTests
    fields = '__all__'
    template_name = 'accounting/additionaltests_form.html'

    def get_success_url(self):
        # Redirect to the associated MedicalRecord detail page
        return reverse_lazy('medicalrecord_detail', kwargs={'pk': self.object.medical_record.pk})


@method_decorator(role_required(['admin']), name='dispatch')
class AdditionalTestsUpdateView(UpdateView):
    model = AdditionalTests
    form_class = AdditionalTestsForm
    template_name = 'accounting/additionaltests_form.html'

    def get_success_url(self):
        # Check for 'next' parameter
        next_url = self.request.GET.get('next') or self.request.POST.get('next')
        if next_url:
            if 'medicalrecord' in next_url:
                return next_url  # Redirect to MedicalRecord detail if 'next' points there
            elif 'sportsperson' in next_url:
                return next_url  # Redirect to Sportsperson detail if 'next' points there
        # Default redirect to the associated MedicalRecord detail page
        return reverse_lazy('medicalrecord_detail', kwargs={'pk': self.object.medical_record.pk})


@method_decorator(role_required(['admin']), name='dispatch')
class AdditionalTestsDeleteView(DeleteView):
    model = AdditionalTests
    template_name = 'accounting/additionaltests_confirm_delete.html'

    def get_success_url(self):
        # Store the medical_record.pk before deletion
        medical_record_pk = self.object.medical_record.pk
        # Check for 'next' parameter
        next_url = self.request.GET.get('next') or self.request.POST.get('next')
        if next_url:
            if 'medicalrecord' in next_url:
                return next_url  # Redirect to MedicalRecord detail if 'next' points there
            elif 'sportsperson' in next_url:
                return next_url  # Redirect to Sportsperson detail if 'next' points there
        # Default redirect to the associated MedicalRecord detail page
        return reverse_lazy('medicalrecord_detail', kwargs={'pk': medical_record_pk})


# --- CRUD для Notes ---
class NotesListView(ListView):
    model = Notes
    template_name = 'accounting/notes_list.html'
    context_object_name = 'notes_list'
    paginate_by = 10  # 10 items per page


@method_decorator(role_required(['admin', 'editor']), name='dispatch')
class NotesCreateView(NextUrlMixin, CreateView):
    model = Notes
    form_class = NotesForm
    template_name = 'accounting/notes_create.html'

    def get_initial(self):
        initial = super().get_initial()
        sportsperson_id = self.kwargs.get('sportsperson_id') or self.request.GET.get('sportsperson_id')
        if sportsperson_id:
            sportsperson = get_object_or_404(Sportsperson, pk=sportsperson_id)
            initial['sportsperson'] = sportsperson
        record_id = self.kwargs.get('record_id') or self.request.GET.get('record_id')
        if record_id:
            medical_record = get_object_or_404(MedicalRecord, pk=record_id)
            initial['medical_record'] = medical_record
            initial['sportsperson'] = medical_record.sportsperson
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        sportsperson_id = self.kwargs.get('sportsperson_id') or self.request.GET.get('sportsperson_id')
        record_id = self.kwargs.get('record_id') or self.request.GET.get('record_id')
        if sportsperson_id:
            sportsperson = get_object_or_404(Sportsperson, pk=sportsperson_id)
            kwargs['sportsperson'] = sportsperson
        if record_id:
            medical_record = get_object_or_404(MedicalRecord, pk=record_id)
            kwargs['medical_record'] = medical_record
        return kwargs

    def form_valid(self, form):
        note = form.save(commit=False)
        if form.cleaned_data['medical_record']:
            note.sportsperson = form.cleaned_data['medical_record'].sportsperson
        note.save()
        return super().form_valid(form)

    def get_success_url(self):
        # Use NextUrlMixin to handle the 'next' parameter
        next_url = super().get_success_url()
        if next_url:
            if 'medicalrecord' in next_url:
                return next_url  # Redirect to MedicalRecord detail if 'next' points there
            elif 'sportsperson' in next_url:
                return next_url  # Redirect to Sportsperson detail if 'next' points there
        # Default redirect to the associated MedicalRecord detail page
        return reverse_lazy('medicalrecord_detail', kwargs={'pk': self.object.medical_record.pk})

@method_decorator(role_required(['admin', 'editor']), name='dispatch')
class NotesCreateGlobalView(CreateView):
    model = Notes
    fields = '__all__'
    template_name = 'accounting/notes_form.html'

    def get_success_url(self):
        # Redirect to the associated MedicalRecord detail page
        return reverse_lazy('medicalrecord_detail', kwargs={'pk': self.object.medical_record.pk})


@method_decorator(role_required(['admin']), name='dispatch')
class NotesUpdateView(UpdateView):
    model = Notes
    form_class = NotesForm
    template_name = 'accounting/notes_form.html'

    def get_success_url(self):
        # Check for 'next' parameter
        next_url = self.request.GET.get('next') or self.request.POST.get('next')
        if next_url:
            if 'medicalrecord' in next_url:
                return next_url  # Redirect to MedicalRecord detail if 'next' points there
            elif 'sportsperson' in next_url:
                return next_url  # Redirect to Sportsperson detail if 'next' points there
        # Default redirect to the associated MedicalRecord detail page
        return reverse_lazy('medicalrecord_detail', kwargs={'pk': self.object.medical_record.pk})


@method_decorator(role_required(['admin']), name='dispatch')
class NotesDeleteView(DeleteView):
    model = Notes
    template_name = 'accounting/notes_confirm_delete.html'

    def get_success_url(self):
        # Store the medical_record.pk before deletion
        medical_record_pk = self.object.medical_record.pk
        # Check for 'next' parameter
        next_url = self.request.GET.get('next') or self.request.POST.get('next')
        if next_url:
            if 'medicalrecord' in next_url:
                return next_url  # Redirect to MedicalRecord detail if 'next' points there
            elif 'sportsperson' in next_url:
                return next_url  # Redirect to Sportsperson detail if 'next' points there
        # Default redirect to the associated MedicalRecord detail page
        return reverse_lazy('medicalrecord_detail', kwargs={'pk': medical_record_pk})
