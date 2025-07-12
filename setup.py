#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from setuptools import setup, find_packages

# read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# read the contents of requirements.txt
with open("requirements.txt") as f:
    requirements = f.read().strip().split("\n")

setup(
    name="sales_agent_commission",
    version="1.0.0",
    description="Comprehensive Sales Agent Commission Management System for ERPNext",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Frappe Technologies Pvt. Ltd.",
    author_email="support@frappe.io",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Frappe",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Accounting",
    ],
    keywords=["erpnext", "commission", "sales", "agent"],
    project_urls={
        "Homepage": "https://github.com/frappe/sales_agent_commission",
        "Repository": "https://github.com/frappe/sales_agent_commission",
        "Documentation": "https://docs.frappe.io/apps/sales_agent_commission",
        "Issues": "https://github.com/frappe/sales_agent_commission/issues",
    },
)