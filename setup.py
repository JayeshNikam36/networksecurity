from setuptools import setup, find_packages
from typing import List

def get_requirements() -> List[str]:
    requirement_lst:List[str] = []
    try:
        with open("requirements.txt", 'r') as file:
            lines = file.readlines()
            for line in lines:
                requirements = line.strip()
                if requirements and requirements != '-e .':
                    requirement_lst.append(requirements)
    except FileNotFoundError:
        print("Warning: requirements.txt not found. No requirements loaded.")

    return requirement_lst

setup(
    name='NetworkSecurity',
    version='0.1',
    author='Jayesh Nikam',
    author_email='jayeshnikam04@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements()
)