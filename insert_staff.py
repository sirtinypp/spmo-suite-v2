
import os

index_path = r'c:\Users\Aaron\spmo-suite - Copy\spmo_website\templates\index.html'
staff_path = r'c:\Users\Aaron\spmo-suite - Copy\staff_section.html'

with open(index_path, 'r', encoding='utf-8') as f:
    index_content = f.read()

with open(staff_path, 'r', encoding='utf-8') as f:
    staff_content = f.read()

# Target the end of the leadership section
# We know it ends with specific tags before the Inspection Calendar or just look for the marker.
# The previous swap moved Leadership to be AFTER News.
# So the order is: News -> Leadership -> Inspection Calendar (maybe).
# Let's check what comes after Leadership.
# "Office Leadership" section starts with <section id="leadership"
# We find the closing </section> for that id.

leadership_start = index_content.find('id="leadership"')
if leadership_start == -1:
    print("Could not find leadership section start")
    exit(1)

# Find the next </section> after leadership_start
leadership_end = index_content.find('</section>', leadership_start)
if leadership_end == -1:
    print("Could not find leadership section end")
    exit(1)

# Include the closing tag length
insert_pos = leadership_end + len('</section>')

# Insert existing content + new lines + staff content + rest
new_content = index_content[:insert_pos] + '\n\n' + staff_content + index_content[insert_pos:]

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Successfully inserted Staff section.")
