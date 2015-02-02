from setuptools import setup, find_packages
import os

name = "lunch_app"
version = "0.5.5"


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name=name,
    version=version,
    description="STX Lunch server",
    long_description=read('README.md'),
    classifiers=[],
    keywords="",
    author="",
    author_email='',
    url='',
    license='MIT',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Flask',
        'Flask-RESTful',
        'Flask-SQLAlchemy',
        'Flask-Login',
        'python-social-auth',
     #   'psycopg2',
        'Flask-Admin',
        'Flask-Mail',
        'Flask-Script',
        'Flask-Migrate',
        'Flask-Celery3',
    ],
    entry_points="""
    [console_scripts]
    flask-ctl = lunch_app.script:run
    """,
)
