from setuptools import setup, find_packages

setup(
    name="drweb-plugin-ai-selector",
    version="1.0.0",
    description="AI-powered element selector plugin for DR Web Engine",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="DR Web Engine Team",
    author_email="support@drwebengine.com", 
    homepage="https://github.com/starlitlog/drweb-plugin-ai-selector",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        # "dr-web-engine>=0.10.0",  # Commented out for local development
        "requests>=2.25.0",
        "pydantic>=2.0.0"
    ],
    entry_points={
        'drweb.plugins': [
            'ai-selector = drweb_plugin_ai_selector.plugin:AISelectorPlugin',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.10",
    keywords="web scraping, ai, element selection, automation",
)