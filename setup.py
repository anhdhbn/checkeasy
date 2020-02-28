from setuptools import setup, find_packages

requirements = ["beautifulsoup4", "cloudscraper", "lxml"]

setup(
    name='checkeasy',
    version='0.0.1',
    description='Check hyip easy',
    url='git@github.com:anhdhbn/checkeasy.git',
    author='Anh DH',
    author_email='anhdhbn@gmail.com',
    license='unlicense',
    packages=find_packages(),
    install_requires=requirements,
    zip_safe=False
)