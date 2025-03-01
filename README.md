# DevHub
A site with many feature such as video calling, text chat, a meeting location finder, and other useful tools to help people find projects to contribute to and to find people to contribute to your own projects.
# Instructions
-create virtual environment (python -m venv .venv) .venv is the name of your virtual environment
-activate virtual environment (.\/.venv/Scripts/activate.ps1)
-py .\manage.py migrate (update models)
-pip install -r requirements.txt (Install in the virtual environment)
-py .\manage.py runserver (start servers)
-docker run --rm -p 6379:6379 redis:7