try:
    from setuptools import setup, find_packages
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
        name='fcd',
        description="Fast cognate detection with skip n-grams and bipartite networks",
        author='',
        url='https://github.com/lingpy/fcd',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
        ],
        version='0.0.1',
        packages=find_packages(where='src'),
        package_dir={'': 'src'},
        install_requires=['wheel', 'lingpy', 'networkx', 'igraph-python'],
        keywords="historical linguistics, computational linguistics, computer-assisted language comparison"
        )
