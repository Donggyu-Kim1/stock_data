from setuptools import setup, find_packages

setup(
    name="stock_data",
    version="0.1",
    packages=find_packages(),
    install_requires=["pymysql", "SQLAlchemy", "python-dotenv"],
)
