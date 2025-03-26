from setuptools import setup, find_packages

setup(
    name="conversor-xml",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "Flask==2.0.3",
        "Flask-WTF==1.0.1",
        "Werkzeug==2.0.3",
        "Jinja2==3.0.3",
        "gunicorn==20.1.0",
        "requests==2.27.1",
    ],
) 