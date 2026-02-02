import sys
sys.path.append('/app')
import os
import django
from django.conf import settings
from django.template import Template, Context, Engine

def test_template():
    # Configure minimal settings for Template Engine
    if not settings.configured:
        settings.configure(
            TEMPLATES=[{
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'APP_DIRS': True, 
            }],
            INSTALLED_APPS=['django.contrib.humanize', 'supplies'],
        )
    django.setup()

    # Read the file
    path = '/app/suplay_app/supplies/templates/supplies/app_status.html'
    # We must read from the LOCAL file since we are simulating the fix locally before deploy
    # But wait, this script runs on REMOTE usually. 
    # To check locally (on Windows), I need to point to the local file.
    
    local_path = r"c:\Users\Aaron\spmo-suite - Copy\suplay_app\supplies\templates\supplies\app_status.html"
    
    with open(local_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"--- Validating Template: {local_path} ---")
    try:
        # Create a Template object - this parses the syntax
        # We need to strip specific tags that valid without context or mocks?
        # Actually, 'extends' and 'load' might fail if apps aren't setup.
        # So we just test the SYNTAX, not the rendering.
        
        # NOTE: 'extends' requires the parent file to exist.
        # We can mock the parent or just try to compile a string that removes the extends?
        # Let's try compiling the FULL valid file but we need to mock the environment.
        
        # Hack strategy: Remove {% extends %} to test the rest of the body syntax independent of parent.
        # Remove {% load %} or keep if we installed 'django.contrib.humanize' (which we did).
        
        # Simplified content for syntax check
        # content = "{% load humanize %}" + content.split("{% block content %}")[1].split("{% endblock %}")[0]
        
        # Better: use Engine to compile string
        engine = Engine(
             libraries={'humanize': 'django.contrib.humanize.templatetags.humanize'},
             builtins=['django.templatetags.static']
        )
        
        t = engine.from_string(content)
        print("SUCCESS: Template syntax is Valid.")
        
    except Exception as e:
        print(f"ERROR: Template Syntax Error Found:\n{e}")

if __name__ == '__main__':
    test_template()
