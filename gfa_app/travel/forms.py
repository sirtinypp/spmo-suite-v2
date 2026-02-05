from django import forms
from .models import BookingRequest


# 1. USER: Initial Request Form
class BookingRequestForm(forms.ModelForm):
    # Explicitly set required=False for checkboxes so "Unchecked" is valid
    is_official = forms.BooleanField(required=False)
    avail_insurance = forms.BooleanField(required=False)
    agreed_to_policy = forms.BooleanField(required=True)

    class Meta:
        model = BookingRequest
        # Exclude system/admin fields and document uploads for the first step
        exclude = [
            "status",
            "created_at",
            "doc_signed_slip",
            "doc_travel_order",
            "doc_gov_id",
            "doc_itinerary",
            "doc_previous_gfa",
            "booking_reference_no",
            "doc_flight_ticket",
            "doc_voucher",
            "admin_instructions",
            "ticket_issued_at",
        ]

        widgets = {
            "birthday": forms.DateInput(attrs={"type": "date"}),
            "departure_date": forms.DateInput(attrs={"type": "date"}),
            "departure_time": forms.TimeInput(attrs={"type": "time"}),
            "return_date": forms.DateInput(attrs={"type": "date"}),
            "return_time": forms.TimeInput(attrs={"type": "time"}),
            "approval_date": forms.DateInput(attrs={"type": "date"}),
            "purpose": forms.Textarea(attrs={"rows": 3}),
            "special_requests": forms.Textarea(attrs={"rows": 2}),
            "remarks": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Tailwind styling
        for field in self.fields:
            if isinstance(self.fields[field].widget, forms.CheckboxInput):
                self.fields[field].widget.attrs.update(
                    {"class": "w-5 h-5 text-blue-600 rounded focus:ring-blue-500"}
                )
            else:
                self.fields[field].widget.attrs.update(
                    {
                        "class": "w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-900 focus:border-transparent outline-none transition duration-200 text-sm"
                    }
                )


# 2. USER: Document Upload Form
class BookingUploadForm(forms.ModelForm):
    class Meta:
        model = BookingRequest
        fields = [
            "doc_signed_slip",
            "doc_travel_order",
            "doc_gov_id",
            "doc_itinerary",
            "doc_previous_gfa",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer border border-slate-300 rounded-lg bg-slate-50"
                }
            )
            # Make the first 4 required in the form logic
            if field != "doc_previous_gfa":
                self.fields[field].required = True


# 3. ADMIN: Attach Ticket Form
class AdminBookingForm(forms.ModelForm):
    class Meta:
        model = BookingRequest
        fields = [
            "booking_reference_no",
            "total_amount",
            "doc_flight_ticket",
            "doc_voucher",
            "admin_instructions",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-600 outline-none text-sm"
                }
            )
            if field in ["doc_flight_ticket", "doc_voucher"]:
                self.fields[field].widget.attrs.update(
                    {
                        "class": "block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100 cursor-pointer border border-slate-300 rounded-lg bg-white"
                    }
                )
        self.fields["admin_instructions"].widget.attrs.update(
            {
                "rows": 4,
                "placeholder": "Enter check-in reminders, terminal details, etc.",
            }
        )
        self.fields["total_amount"].widget.attrs.update({"placeholder": "0.00"})
