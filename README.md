# B-leave
A repo to store the streamlit app which will make up the B-leave webapp.

# Setup
Below are a set of instruction on how to set up the various tools and services required.

## Python virtual environment
All of the following commands should be run in a terminal on a machine with python installed a python download can be found [here](https://www.python.org/downloads/).
1) Create the virtual environment:
```
py -m venv .venv
```
2) Activate the virtual enviornment:
```
.\.venv\Scripts\activate
```
3) Done. It is as easy as that!
Bonus step is to install of all the required python packages from the requirements.txt
- Install the requirements:
```
pip install -r requirements.txt
```

## Run the Streamlit app
1) Run the app
```
streamlit run app.py
```