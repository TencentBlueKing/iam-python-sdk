import os

import setuptools

here = os.path.abspath(os.path.dirname(__file__))

long_description = "bk-iam python sdk"

requires = [
    "six>=1.11.0",
    "cachetools==3.1.1",
    "requests",
    "curlify==2.2.1",
]

about = {}
with open(os.path.join(here, "iam", "__version__.py"), "r") as f:
    exec(f.read(), about)

setuptools.setup(
    name="bk-iam",
    version=about["__version__"],
    author="TencentBlueKing",
    author_email="contactus_bk@tencent.com",
    description="bk-iam python sdk",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TencentBlueKing/iam-python-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/TencentBlueKing/iam-python-sdk/issues",
    },
    packages=setuptools.find_packages(),
    install_requires=requires,
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, <4",
)
