from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name="wrapper-vjwhats",
    license="MIT",
    version="0.0.4",
    author="little_renan",
    author_email="renanrodrigues7110@gmail.com",
    description="Wrapper for vjwhats library to send messages and sent messages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Renan-RodriguesDEV/wrapper-vjwhats",
    packages=find_packages(),
    install_requires=["selenium>=4.33.0", "clipboard>=0.0.4"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
