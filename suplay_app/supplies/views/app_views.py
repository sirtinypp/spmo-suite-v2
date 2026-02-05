from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from ..models import AnnualProcurementPlan

# --- APP MODULE VIEWS ---


@login_required
def my_app_status(request):
    # FIX: Use UserProfile instead of Session/Placeholder
    user_dept = None
    if hasattr(request.user, "profile"):
        user_dept = request.user.profile.department

    if not user_dept:
        # Fallback or empty if no profile
        allocations = AnnualProcurementPlan.objects.none()
    else:
        allocations = (
            AnnualProcurementPlan.objects.filter(
                department=user_dept, year=timezone.now().year
            )
            .select_related("product", "product__category")
            .order_by("product__category__name", "product__name")
        )

    return render(request, "supplies/app_status.html", {"allocations": allocations})
