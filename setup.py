from setuptools import setup,find_packages

setup(
        name = "drug_cycling",
        version="0.0.1",
        author="Devin Greene",
        author_email="devin@greene.cz",
        description="Optimal drug cycling treatement",
        packages = find_packages(exclude = ( 'tests' ) ),
        python_requires=">=3.6"
        )
