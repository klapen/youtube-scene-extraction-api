# YouYube scene extraction api

API for extracting and serving extracted scenes from youtube videos

## Technologies used
* **[Virtualenv](https://virtualenv.pypa.io/en/stable/)**
* **[Autoenv](https://github.com/kennethreitz/autoenv)**
* **[Python3](https://www.python.org/downloads/)**
* **[Flask](flask.pocoo.org/)**
* **[Flask-RESTful](https://flask-restful.readthedocs.io/en/latest/index.html)**
* Minor dependencies can be found in the requirements.txt file on the root folder.


## Installation / Usage
* First ensure you have python3 globally installed in your computer. If not, you can get python3 [here](https://www.python.org).
* After this, ensure you have installed virtualenv globally as well. If not, run this:
    ```
        $ pip install virtualenv
    ```
* Git clone this repo to your PC
    ```
        $ git clone https://github.com/klapen/youtube-scene-extraction-api.git
    ```

* #### Dependencies
    1. Cd into your the cloned repo as such:
        ```
        $ cd youtube-scene-extraction-api
        ```

    2. Create and fire up your virtual environment in python3:
        ```
        $ virtualenv -p python3 venv
        $ pip install autoenv
        ```

* #### Environment Variables
    Create a .env file and add the following:
    ```
    source venv/bin/activate
    export SECRET="some-very-long-string-of-random-characters"
    export APP_SETTINGS="development"
    ```

    To create SECRET varible, you can use the command:
    ```
    $ openssl rand -base64 64
    ```

    Save .env file, cd out of the directory and back in. `Autoenv` will automagically set the variables.

* #### Install your requirements
    ```
    (venv)$ pip install -r requirements.txt
    ```

* #### Running It
    On your terminal, run the server using this one simple command:
    ```
    (venv)$ flask run
    ```
    You can now access the app on your local browser by using
    ```
    http://localhost:5000/youtube-scene-extraction-api/
    ```
    Or test using Postman