from setuptools import setup, find_packages

setup(
    name="web_engine",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "playwright",
        "pydantic",
        "json5",
        "pyyaml",
        "pytest",
        "pytest-playwright",
    ],
    entry_points={
        "console_scripts": [
            "web_engine=dr_web_engine.cli:main",
        ],
    },
)
