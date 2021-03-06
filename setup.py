from setuptools import setup, find_packages

setup(
    name='Search Recommender',
    version='0.2',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask',
        'SQLAlchemy',
        'Celery',
        'Flask-RESTful',
    ]
)
