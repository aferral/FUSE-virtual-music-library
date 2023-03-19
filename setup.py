import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
        name='aferral_fvml', version='0.1',
        author="aferral",
        author_email="anferrad@dcc.uchile.cl",
        description="Fuse music library. All your music in a virtual file system",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/aferral/FUSE-virtual-music-library",
        packages=setuptools.find_packages(),
        classifiers=["Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent"],
 )
