"""Install file for llmpeg."""
from setuptools import setup, find_packages

setup(
    name="llmpeg",
    version="0.1.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # Dependencies here, e.g., 'requests'
    ],
    entry_points={
        "console_scripts": [
            "llmpeg = llmpeg.main:main",
        ],
    },
)
