import setuptools

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='srt',
    version='0.1.0',
    author='Anthony Mercurio',
    author_email='anthony.mercurio@protonmail.com',
    description='A simple tool to conduct iterative-based testing on the Sukima API.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/harubaru/sukima-research-tool',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'aiohttp',
        'pydantic',
        'typing'
    ]
)