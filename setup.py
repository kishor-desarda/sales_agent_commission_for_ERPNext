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
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in sales_agent_commission/__init__.py
from sales_agent_commission import __version__ as version

setup(
    name="sales_agent_commission",
    version=version,
    description="Comprehensive Sales Agent Commission Management System",
    long_description="""
	# Sales Agent Commission Management System
	
	A comprehensive, industry-standard commission management system for ERPNext that provides:
	
	- Complete agent master with item group-wise commission rates
	- Payment reconciliation logic (commission due only after payment receipt)
	- Sales Partner integration to resolve confusion
	- Complete audit trail and compliance features
	- Agent visibility of pending invoices and commission status
	- Multi-currency and foreign exchange support
	- Tiered commission structures
	- Automated commission calculations and payments
	
	Built by sales, finance, and ERPNext experts for industrial sales scenarios.
	""",
    long_description_content_type="text/markdown",
    author="Frappe Technologies Pvt. Ltd.",
    author_email="support@frappe.io",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Framework :: Frappe",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="erpnext frappe commission sales agent accounting finance",
    project_urls={
        "Documentation": "https://github.com/frappe/sales_agent_commission/blob/main/README.md",
        "Source": "https://github.com/frappe/sales_agent_commission",
        "Tracker": "https://github.com/frappe/sales_agent_commission/issues",
    },
)