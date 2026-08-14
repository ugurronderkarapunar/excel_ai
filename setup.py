from setuptools import setup, find_packages

setup(
    name="automated-data-analyst",
    version="1.0.0",
    description="Automated Data Analysis, BI, and Statistics Dashboard",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.32",
        "pandas>=2.0",
        "numpy>=1.24",
        "scipy>=1.10",
        "plotly>=5.18",
        "openpyxl>=3.1",
        "xlsxwriter>=3.1",
        "pyarrow>=14.0",
        "statsmodels>=0.14",
    ],
    python_requires=">=3.11",
    include_package_data=True,
)
