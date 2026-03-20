from django.contrib.auth.decorators import login_required
from django.shortcuts import render,get_object_or_404
from .models import Course, Video, Purchase, VideoProgress
from django.shortcuts import redirect
import razorpay
from django.conf import settings
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

def ping(request):
    return HttpResponse("OK")

@csrf_exempt   # ✅ keep this for now (avoids 400 issue)
@login_required
def verify_payment(request):

    if request.method != "POST":
        return JsonResponse({"status": "invalid request"})

    try:
        data = json.loads(request.body)

        payment_id = data.get("razorpay_payment_id")
        order_id = data.get("razorpay_order_id")
        signature = data.get("razorpay_signature")
        course_id = data.get("course_id")

        if not all([payment_id, order_id, signature, course_id]):
            return JsonResponse({"status": "missing data"})

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        # 🔐 Verify payment
        client.utility.verify_payment_signature({
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature
        })

        # ✅ Get course safely
        course = get_object_or_404(Course, id=course_id)

        # ✅ Prevent duplicate purchase
        Purchase.objects.get_or_create(
            user=request.user,
            course=course
        )

        return JsonResponse({"status": "success"})

    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({"status": "failed"})

    except Exception as e:
        print("Verification Error:", e)
        return JsonResponse({"status": "error"})

def course_list(request):

    courses = Course.objects.all()

    return render(request,"course_list.html",{"courses":courses})



@login_required
def course_detail(request, course_id):

    course = get_object_or_404(Course, id=course_id)

    # ✅ CHECK IF USER PURCHASED THIS COURSE
    has_access = Purchase.objects.filter(
        user=request.user,
        course=course
    ).exists()

    # 🚫 BLOCK ACCESS
    if not has_access:
        return render(request, "access_denied.html", {"course": course})

    # ✅ NORMAL FLOW
    videos = Video.objects.filter(course=course)

    video_progress_queryset = VideoProgress.objects.filter(user=request.user)

    video_progress_dict = {
        vp.video.id: vp.watched_seconds for vp in video_progress_queryset
    }

    context = {
        'course': course,
        'videos': videos,
        'video_progress': video_progress_dict
    }

    return render(request, 'course_detail.html', context)


@login_required
def buy_course(request, course_id):
    try:
        course = get_object_or_404(Course, id=course_id)

        if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
            return HttpResponse("Razorpay keys not configured")

        client = razorpay.Client(auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        ))

        amount = int(course.price * 100)

        payment = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })

        return render(request, "buy_course.html", {
            "course": course,
            "payment": payment,
            "razorpay_key": settings.RAZORPAY_KEY_ID
        })

    except Exception as e:
        return HttpResponse(f"ERROR: {str(e)}")

@csrf_exempt
def payment_success(request):

    if request.method == "POST":

        course_id = request.POST.get("course_id")

        course = Course.objects.get(id=course_id)

        Purchase.objects.get_or_create(
            user=request.user,
            course=course
        )

        return redirect("course_detail", course_id=course.id)

def my_courses(request):

    purchases = Purchase.objects.filter(user=request.user)

    return render(request,"my_courses.html",{
        "purchases":purchases
    })    

def save_progress(request):

    if request.method == "POST":

        data = json.loads(request.body)

        video_id = data.get("video_id")
        seconds = data.get("seconds")

        video = Video.objects.get(id=video_id)

        progress, created = VideoProgress.objects.get_or_create(
            user=request.user,
            video=video
        )

        progress.watched_seconds = seconds
        progress.save()

        return JsonResponse({"status": "saved"})

    return JsonResponse({"status": "error"})



def course_completion(user,course):

    total = Video.objects.filter(course=course).count()

    completed = VideoProgress.objects.filter(
        user=user,
        video__course=course,
        completed=True
    ).count()

    return int((completed/total)*100)

def analytics(request):

    total_courses = Course.objects.count()

    total_students = User.objects.count()

    total_purchases = Purchase.objects.count()

    total_progress = VideoProgress.objects.count()

    return render(request,"analytics.html",{

        "courses":total_courses,
        "students":total_students,
        "purchases":total_purchases,
        "progress":total_progress

    })   




def admin_dashboard(request):

    courses = Course.objects.count()
    videos = Video.objects.count()
    students = User.objects.count()
    purchases = Purchase.objects.count()

    revenue = sum([p.course.price for p in Purchase.objects.select_related("course")])

    # Monthly sales
    monthly_sales = (
        Purchase.objects
        .annotate(month=TruncMonth("created_at"))   # change to date field if you have one
        .values("month")
        .annotate(count=Count("id"))
    )

    labels = []
    data = []

    for item in monthly_sales:
        labels.append(str(item["month"]))
        data.append(item["count"])

    context = {
        "courses": courses,
        "videos": videos,
        "students": students,
        "purchases": purchases,
        "revenue": revenue,
        "labels": labels,
        "data": data
    }

    return render(request, "admin/dashboard.html", context)           