from pathlib import Path
from setuptools import find_packages, setup


ROOT = Path(__file__).parent

setup(
    name="promptx-ai-safety",
    version="1.0.0",
    description="A modular AI safety pipeline for detecting risky LLM prompts.",
    long_description=(ROOT / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    py_modules=["app", "demo_dashboard"],
    include_package_data=True,
    install_requires=[
        "Flask>=3.1,<4",
        "requests>=2.32,<3",
        "spacy>=3.8,<4",
        "nltk>=3.9,<4",
    ],
    python_requires=">=3.10",
)
