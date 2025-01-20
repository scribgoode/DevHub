# DevHub
 a site where you can go to find other real people to be friend and do a project with that bettert ensures you complete a project
# Instructions
-create virtual environment (python -m venv .venv) .venv is the name of your virtual environment
-activate virtual environment (.\/.venv/Scripts/activate.ps1)
-py .\manage.py migrate (update models)
-pip install -r requirements.txt (Install in the virtual environment)
-py .\manage.py runserver (start servers)
-docker run --rm -p 6379:6379 redis:7