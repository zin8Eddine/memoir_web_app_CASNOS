# Thème: Conception et réalisation d'une application web pour la gestion de la consommation des médicaments des assurés

Mémoire de fin de Stage En vue de l’obtention d’un Diplôme 
de Technicien Supérieur en Informatique


## Requirements

- Python 3.11.4
- Django  4.2.1

## Installation


1. Clone the repository:

    ```bash
    git clone https://github.com/zin8Eddine/memoir_web_app_CASNOS.git
    ```

2. Change into the project directory:

    ```bash
    cd memoir_web_app_CASNOS/web_app_CASNOS
    ```    
3. Create a virtual environment:

    ```bash
    python -m venv venv
    ```

    This command creates a virtual environment named `venv` in your project directory.

4. Activate the virtual environment:

    - On Windows:

        ```bash
        venv\Scripts\activate
        ```

    - On Unix or MacOS:

        ```bash
        source venv/bin/activate
        ```

    After activation, your terminal prompt should change, indicating that the virtual environment is active.

### Installation

1. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

    This command installs the required Python packages specified in the `requirements.txt` file.

### Database Setup

1. Apply initial database migrations:

    ```bash
    python manage.py migrate
    ```

2. Create an admin user:

    ```bash
    python manage.py createsuperuser
    ```

    Follow the prompts to create an admin user.

### Running the Development Server

Start the Django development server:

```bash
python manage.py runserver
