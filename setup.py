"""
Flask-SQLAFixtures

"""
from setuptools import setup

setup(
    name='Flask-SQLAFixtures',
    version='1.0',
    url='',
    license='MIT',
    author='Jason Job',
    author_email='jasonwadejob@gmail.com',
    description='',
    packages=['flask_sqlafixtures'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'click',
        'pandas',
        'numpy',
        'simplejson',
        'xlrd'
    ],
    tests_require=[
        'pytest'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
