import os
from setuptools import setup, find_packages

# Get the directory of the current file (setup.py)
current_directory = os.path.dirname(__file__)
# Construct the path to README.md in the parent directory
readme_path = os.path.join(current_directory, '..', 'README.md')

setup(
    name='smart_email_assistant',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'google-auth',
        'google-api-python-client',
        'google-generativeai',
        'fastapi',
        'pandas',
        'beautifulsoup4',
        'python-dotenv',
        'pydantic',
        'uvicorn',
        'google-auth-oauthlib',
        'python-dateutil' # Added for date parsing in ThreadAnalyzer and DataProcessor
    ],
    entry_points={
        'console_scripts': [
            'smart-email-assistant-backend=smart_email_assistant.backend.src.main:main',
            'smart-email-assistant-api=smart_email_assistant.backend.src.app:main', # Added for API
        ],
    },
    python_requires='>=3.9',
    author='Cline',
    description='Backend for Smart Email Assistant Tool',
    long_description=open(readme_path, encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/your-username/smart-email-assistant', # Replace with actual repo URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
