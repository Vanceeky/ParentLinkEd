# ParentLinkED

## Prerequisites

Before you begin, ensure you have the following installed:

- [Python 3.11.5](https://www.python.org/downloads/release/python-3115/)
- [pip](https://pip.pypa.io/en/stable/) - Python's package installer.

## Setting Up the Environment

1. **Install virtualenv**
    - Open your command prompt (cmd) and type:
      pip install virtualenv

2. **Create a virtual environment**
    - Navigate to your project directory and run:
      virtualenv env

3. **Activate the virtual environment**
    - On Windows:
      env\Scripts\activate

4. **Install the required libraries**
    - Ensure you have a `requirements.txt` file in your project directory. Run the following command to install all necessary dependencies:
      pip install -r requirements.txt
    

## Running the Server

After installing the dependencies, you can start the server with:
python manage.py runserver