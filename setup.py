"""OntologyOps package setup."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip()
        for line in fh
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="ontologyops",
    version="1.0.0",
    author="Pankaj Kumar",
    author_email="cloudpankaj@example.com",
    description="Production-grade infrastructure for AI agent ontology version control, testing, and deployment",
    keywords=["ontology", "devops", "version-control", "testing", "cicd", "AI", "semantic-web", "ai-agents", "mlops"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cloudbadal007/ontologyops",
    project_urls={
        "Bug Tracker": "https://github.com/cloudbadal007/ontologyops/issues",
        "Documentation": "https://ontologyops.readthedocs.io",
        "Source Code": "https://github.com/cloudbadal007/ontologyops",
        "Changelog": "https://github.com/cloudbadal007/ontologyops/blob/main/CHANGELOG.md",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "docs"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Version Control",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "isort>=5.12",
            "flake8>=6.0",
            "mypy>=1.0",
            "pre-commit>=3.0",
        ],
        "docs": [
            "mkdocs>=1.4",
            "mkdocs-material>=9.0",
            "mkdocstrings[python]>=0.20",
        ],
        "monitoring": [
            "prometheus-client>=0.16",
        ],
    },
    entry_points={
        "console_scripts": [
            "ontologyops=ontologyops.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
