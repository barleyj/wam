from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='wam',
    version='0.1',
    py_modules=['wam'],
    install_requires=requirements,
    entry_points='''
        [console_scripts]
        wam=wam:main
    ''',
)
