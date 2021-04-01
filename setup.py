from setuptools import find_packages, setup  # type: ignore

setup(
    name='yaml-cv-py',
    version='1.0.0',
    description='YAMLによる履歴書作成スクリプト',
    description_content_type='',
    long_description=open('README.md', encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    url='https://github.com/toritamantaro/yaml_cv_py',
    author='toritamantaro',
    packages=find_packages(),
    python_requires='>=3.8',
    include_package_data=True,
    license='MIT',
    install_requires=[ # requirements.txtに記述し読込でも良
        'PyYAML==5.4.1',
        'reprotlab==3.5.59'
    ],
    scripts=['make_cv.py']
)