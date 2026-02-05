from supplies.models import AnnualProcurementPlan, Department

print("Total APP Allocations:", AnnualProcurementPlan.objects.count())
print("For 2025:", AnnualProcurementPlan.objects.filter(year=2025).count())
print("For 2026:", AnnualProcurementPlan.objects.filter(year=2026).count())
print("Total Departments:", Department.objects.count())
