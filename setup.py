from distutils.core import setup

setup(
    name='ILOT',
    version='1.0',
    author='Nicolas Danjean',
    author_email='nicolas@biodigitals.com',
    packages=['ilot',
              'ilot.core',
              'ilot.meta',
              'ilot.cloud',
              'ilot.medias',
              'ilot.data',
              'ilot.grammar',
              'ilot.rules',
              'ilot.scenarios',
              'ilot.management',
              'ilot.migrations',
              'ilot.templatetags',
              'ilot.views',
              'ilot.webhooks'
              ],
    package_data={'ilot': ['ilot/templates/*', 'ilot/static/*']},
    scripts=[],
    url='https://github.com/biodigitals/ilot/',
    license='LICENSE.txt',
    description='',
    long_description="""ILOT is a django application
meant to manage item structure
and interactions workflows using a action status rule system.""",
    install_requires=[
        "python-dateutil",
        "python-magic>=0.4.6",
        "pytz>=2014.7",
        "Django==1.11",
        "django-markdown-deux",
        "django-mathfilters",
        "six>=1.8.0",
        'Pillow',
        'tornado==4.4',
        "django-imagekit",
        'django-mailjet',
        'captcha',
        'mkdocs',
        'pydenticon',
        'djangorestframework',
        'django-filter',
        'django-rest-swagger',
        'requests-html',
        'circus',
        'web3',
        'psycopg2-binary'
    ],
    entry_points = {
        'console_scripts': [
            'ilot = ilot.manage:main',
        ],
        'mkdocs.plugins': [
            'ilot = ilot.mkdocs:MkdocsPlugin',
        ],
    },
)
