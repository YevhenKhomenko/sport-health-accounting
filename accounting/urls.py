from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounting import views
from accounting.views import MedicalRecordCreateGlobalView, medicalrecord_select_unassigned, assign_medicalrecord, \
    registration_view

urlpatterns = [

    # path('select2/', include('django_select2.urls')),

    # Авторизація
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', registration_view, name='register'),


    # Стартова сторінка – dashboard
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Sportsperson (спортсмени)
    path('sportsperson/list/', views.sportsperson_list, name='sportsperson_list'),
    path('sportsperson/<int:pk>/', views.sportsperson_detail, name='sportsperson_detail'),
    path('sportsperson/add/', views.SportspersonCreateView.as_view(), name='sportsperson_add'),
    path('sportsperson/<int:pk>/edit/', views.SportspersonUpdateView.as_view(), name='sportsperson_edit'),
    path('sportsperson/<int:pk>/delete/', views.SportspersonDeleteView.as_view(), name='sportsperson_delete'),
    path('sportsperson/<int:sportsperson_pk>/add-trainer/', views.SportspersonAddTrainerView.as_view(), name='sportsperson_add_trainer'),
    path('sportsperson/<int:sportsperson_pk>/remove-trainer/<int:trainer_pk>/', views.SportspersonRemoveTrainerView.as_view(), name='sportsperson_remove_trainer'),
    path('sportsperson/<int:sportsperson_pk>/add-organization/', views.SportspersonAddOrganizationView.as_view(), name='sportsperson_add_organization'),
    path('sportsperson/<int:sportsperson_pk>/remove-organization/<int:organization_pk>/', views.SportspersonRemoveOrganizationView.as_view(), name='sportsperson_remove_organization'),

    # Trainer (тренери)
    path('trainer/', views.TrainerListView.as_view(), name='trainer_list'),
    path('trainer/add/', views.TrainerCreateView.as_view(), name='trainer_add'),
    path('trainer/<int:pk>/', views.trainer_detail, name='trainer_detail'),
    path('trainer/<int:pk>/edit/', views.TrainerUpdateView.as_view(), name='trainer_edit'),
    path('trainer/<int:pk>/delete/', views.TrainerDeleteView.as_view(), name='trainer_delete'),

    # Organization (організації)
    path('organization/', views.OrganizationListView.as_view(), name='organization_list'),
    path('organization/add/', views.OrganizationCreateView.as_view(), name='organization_add'),
    path('organization/<int:pk>/', views.organization_detail, name='organization_detail'),
    path('organization/<int:pk>/edit/', views.OrganizationUpdateView.as_view(), name='organization_edit'),
    path('organization/<int:pk>/delete/', views.OrganizationDeleteView.as_view(), name='organization_delete'),

    # MedicalRecord (медичні записи)
    path('medicalrecord/', views.MedicalRecordListView.as_view(), name='medicalrecord_list'),
    path('medicalrecord/add/', MedicalRecordCreateGlobalView.as_view(), name='medicalrecord_add_global'),
    path('medicalrecord/add/<int:sportsperson_id>/', views.MedicalRecordCreateView.as_view(), name='medicalrecord_add'),
    path('medicalrecord/<int:pk>/', views.medicalrecord_detail, name='medicalrecord_detail'),
    path('medicalrecord/<int:pk>/edit/', views.MedicalRecordUpdateView.as_view(), name='medicalrecord_edit'),
    path('medicalrecord/<int:pk>/delete/', views.MedicalRecordDeleteView.as_view(), name='medicalrecord_delete'),
    path('medicalrecord/select_unassigned/', medicalrecord_select_unassigned, name='medicalrecord_select_unassigned'),
    path('medicalrecord/assign/<int:record_pk>/', assign_medicalrecord, name='assign_medicalrecord'),

    # Anthropometry (антропометрія)
    path('anthropometry/', views.AnthropometryListView.as_view(), name='anthropometry_list'),
    path('anthropometry/add/', views.AnthropometryCreateView.as_view(), name='anthropometry_add'),
    path('anthropometry/add/<int:sportsperson_id>/', views.AnthropometryCreateView.as_view(), name='anthropometry_add'),
    path('anthropometry/<int:pk>/', views.anthropometry_detail, name='anthropometry_detail'),
    path('anthropometry/<int:pk>/edit/', views.AnthropometryUpdateView.as_view(), name='anthropometry_edit'),
    path('anthropometry/<int:pk>/delete/', views.AnthropometryDeleteView.as_view(), name='anthropometry_delete'),

    # AdditionalTests (додаткові обстеження)
    path('additionaltests/', views.AdditionalTestsListView.as_view(), name='additionaltests_list'),
    path('additionaltests/add_global/', views.AdditionalTestsCreateGlobalView.as_view(),
         name='additionaltests_add_global'),
    path('additionaltests/add/<int:sportsperson_id>/', views.AdditionalTestsCreateView.as_view(),
         name='additionaltests_add'),
    path('additionaltests/<int:pk>/', views.additionaltests_detail, name='additionaltests_detail'),
    path('additionaltests/<int:pk>/edit/', views.AdditionalTestsUpdateView.as_view(), name='additionaltests_edit'),
    path('additionaltests/<int:pk>/delete/', views.AdditionalTestsDeleteView.as_view(), name='additionaltests_delete'),

    # Notes (примітки)
    path('notes/', views.NotesListView.as_view(), name='notes_list'),
    path('notes/add_global/', views.NotesCreateGlobalView.as_view(), name='notes_add_global'),
    path('notes/add/<int:sportsperson_id>/', views.NotesCreateView.as_view(), name='notes_add'),
    path('notes/<int:pk>/', views.note_detail, name='notes_detail'),
    path('notes/<int:pk>/edit/', views.NotesUpdateView.as_view(), name='notes_edit'),
    path('notes/<int:pk>/delete/', views.NotesDeleteView.as_view(), name='notes_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
