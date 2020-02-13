import sys

try:
    from setuptools import setup
except ImportError:
    print("This project needs setuptools.", file=sys.stderr)
    print("Please install it using your package-manager or pip.", file=sys.stderr)
    sys.exit(1)

from uberspace_takeout import __version__ as version


setup(
    name="uberspace_takeout",
    version=version,
    description="",
    author="uberspace.de",
    author_email="hallo@uberspace.de",
    url="https://github.com/uberspace/takeout",
    packages=["uberspace_takeout", "uberspace_takeout.items",],
    extras_require={"test": ["pyfakefs>=3.6", "pytest-mock",],},
    entry_points={
        "console_scripts": ["uberspace-takeout=uberspace_takeout.__main__:main"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration",
        "Topic :: Security",
        "Topic :: Utilities",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.7",
    ],
    zip_safe=True,
)
