from distutils.core import setup
from piratebay import __version__

setup(
    name="piratebay",
    version=__version__,
    author="sobber",
    author_email="alex.borgert@gmail.com",
    description="A python interface to thepiratebay dot org.",
    license="MIT/X",
    url="http://hg.sobber.org/piratebay",
    long_description="A python interface to thepiratebay dot org.",
    packages=["piratebay"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        ],
)
