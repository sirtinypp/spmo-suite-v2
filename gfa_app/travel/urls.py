from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # --- AUTHENTICATION (New) ---
    # This defines the 'login' URL name that @login_required looks for
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="travel/login.html"),
        name="login",
    ),
    # 5. Logout (Updated to redirect to the new login page)
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    # --- APP VIEWS ---
    # 1. Landing Page (index.html)
    path("", views.index, name="index"),
    # 2. "Book a Flight" Button -> leads to form.html
    path("book/", views.book_flight, name="gfa_create"),
    # 3. "My Bookings" / "Flight Schedules" -> leads to dashboard.html
    path("dashboard/", views.admin_dashboard, name="gfa_dashboard"),
    # 4. Action URL for approving/returning docs
    path("update_status/<int:pk>/", views.update_status, name="update_status"),
    # 6. Print Requisition Slip
    path("print/<int:pk>/", views.print_requisition, name="print_requisition"),
    # 7. Upload Documents (User)
    path("upload/<int:pk>/", views.upload_documents, name="gfa_upload"),
    # 8. Admin Issue Ticket
    path(
        "ticket/process/<int:pk>/",
        views.admin_attach_ticket,
        name="admin_attach_ticket",
    ),
    # 9. Booking Summary (Final View)
    path("summary/<int:pk>/", views.booking_summary, name="booking_summary"),
]
