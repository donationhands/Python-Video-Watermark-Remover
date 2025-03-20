#Initialize a new project
conda create --name flask_env python=3.9
conda activate flask_env
conda install flask
conda install flask  # or django, fastapi, etc.

mkdir my_flask_app
cd my_flask_app

pip freeze > requirements.txt


#Project Structure
https://flask.palletsprojects.com/en/stable/tutorial/layout/#project-layout

https://flask.palletsprojects.com/en/stable/tutorial/factory/#run-the-application
flask --app flaskr run --debug