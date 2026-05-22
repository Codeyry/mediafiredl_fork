from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()


setup(
    name='mediafiredl_fork',
    version='0.1',
    author='Codeyry',
    url='https://github.com/Codeyry',
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4==4.14.3',
        'requests==2.33.1',
        'urllib3==2.6.3',
    ],
    entry_points={
        "console_scripts": [
            "mf-download = mediafiredl_fork:Download",
            "mf-getname = mediafiredl_fork:GetName",
            "mf-bulk-dl = mediafiredl_fork:BulkDownload",
            "mf-getfilelink = mediafiredl_fork:GetFileLink",
            "mf-getfilesize = mediafiredl_fork:GetFileSize",
        ],
    },
    long_description=description,
    long_description_content_type="text/markdown",
)
