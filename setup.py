from setuptools import setup, find_packages


setup(
    name="pre_wigs_validation",
    version="0.1.0",
    description="Pre-WIG Validator for Linux",
    author="steno",
    author_email="steno@amazon.com",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=["requests", "dataclasses", "distro", "PrettyTable"]
    # Maybe include dev dependencies in a txt file
)
