from setuptools import find_packages, setup

setup(
    name="nyust-sso-client",
    version="0.1.1",
    description="A client for NYUST SSO system, providing authenticated access and common API calls.",
    long_description=open("README.md", encoding="utf8").read(),
    long_description_content_type="text/markdown",
    author="jason9294",
    author_email="jason9294@gmail.com",
    url="https://github.com/jason9294/NYUST-SSO-Client",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4 >= 4.12.3",
        "pydantic >= 2.8.2",
        "pytz >= 2024.1",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
