from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    # الجهات المانحة
    path("donors/", views.donor_list, name="donor_list"),
    path("donors/<str:donor_id>/", views.donor_detail, name="donor_detail"),
    path("add-donor/", views.add_donor, name="add_donor"),

    # الجهات المستفيدة
    path("beneficiaries/", views.beneficiary_list, name="beneficiary_list"),
    path("beneficiaries/<str:beneficiary_id>/", views.beneficiary_detail, name="beneficiary_detail"),

    # المنح
    path("add-grant/", views.add_grant, name="add_grant"),
    path("grants/<str:grant_id>/upload-report/", views.upload_grant_report, name="upload_grant_report"),
]
