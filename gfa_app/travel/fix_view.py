import sys
import os

path = r'c:\Users\Aaron\spmo-suite - Copy\gfa_app\travel\views.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = 0
for i, line in enumerate(lines):
    if skip > 0:
        skip -= 1
        continue
    if 'def booking_summary(request, pk):' in line:
        new_lines.append(line)
        new_lines.append('    from .models import TravelTrip, BookingRequest\n')
        new_lines.append('    trip = TravelTrip.objects.filter(pk=pk).first()\n')
        new_lines.append('    booking = trip if trip else get_object_or_404(BookingRequest, pk=pk)\n')
        new_lines.append("    return render(request, 'travel/booking_summary.html', {'booking': booking, 'is_trip': bool(trip)})\n")
        # Skip the next 2 lines (old implementation)
        skip = 2
    else:
        new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("SUCCESS")
