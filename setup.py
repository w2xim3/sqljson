from setuptools import setup, find_packages

setup(
    name="sqljson",
    version="0.1.4",
    packages=find_packages(),
    install_requires=[
        'pandas'
    ],
    entry_points={
        'console_scripts': [
            'sqljson = sqljson.main:main',
        ],
    },
    author="Maxime Paillé",
    author_email="",
    description="A utility to run SQL-like queries on JSON data.",
    license="MIT",
    keywords="json sql",
    url="https://github.com/w2xim3/sqljson",
)
