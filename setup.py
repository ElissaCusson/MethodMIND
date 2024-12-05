from setuptools import find_packages
from setuptools import setup

with open("requirements-dev.txt") as f:
    content = f.readlines()
requirements = [x.strip() for x in content if "git+" not in x]

setup(name='MethodMIND',
      version="0.0.3",
      description="MethodMIND package",
    #   license="To research",
      author="MethodMIND",
    #   author_email="",
    #   url="",
      install_requires=requirements,
      packages=find_packages(),
      test_suite="tests")
