from setuptools import setup, find_packages

setup(
    name="work_chronometer",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Программа для хронометража работы за компьютером",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "PyQt6>=6.4.0",
        "psutil>=5.9.0",
    ],
    extras_require={
        "windows": ["pywin32>=305"],
    },
    entry_points={
        "console_scripts": [
            "work-chronometer=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)