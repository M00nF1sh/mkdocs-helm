import setuptools

with open('docs/README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='mkdocs_helm',
    version="1.0.2",
    author='M00nF1sh',
    author_email='Me_Fortune@qq.com',
    description="An mkdocs plugin for publishing helm repository",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/M00nF1sh/mkdocs_helm",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'mkdocs.plugins': [
            'helm-repo = mkdocs_helm.repository:HelmRepositoryPlugin'
        ]
    }
)
