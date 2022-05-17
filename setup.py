import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="game_of_hits",
    version="0.1.1",
    author="Cong Wang",
    author_email="wangimagine@gmail.com",
    description="A game in which users need to identify hits of SPI images.  ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/carbonscott/game_of_hits",
    keywords = ['Single particle imaging', 'Human baseline'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
