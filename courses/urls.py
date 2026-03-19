from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('courses/', views.course_list, name="courses"),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('buy/<int:course_id>/', views.buy_course, name="buy_course"),
    path('success/<int:course_id>/', views.payment_success, name="payment_success"),
    path('my-courses/', views.my_courses, name="my_courses"),
    path('save-progress/', views.save_progress, name="save_progress"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("verify-payment/", views.verify_payment, name="verify_payment"),
]

# ✅ THIS MUST BE OUTSIDE urlpatterns
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)