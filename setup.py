from setuptools import setup, find_packages

setup(
    name='pytoolbox4dev',
    version='0.0.1',
    description='A collection of handy utility functions for efficient, reproducible python workflows.',
    author='minion057',
    author_email='getit3981@gmail.com',
    url='https://github.com/minion057/python_utils',
    install_requires=['numpy', 'pandas', 'scikit-learn', 'matplotlib', 'pycm'],
    packages=find_packages(exclude=[]),
    keywords=['python', 'python-utils', 'python-dev-tool', 'pytoolbox4dev', 'pycm'],
    python_requires='>=3.4',
    package_data={},
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5,
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)