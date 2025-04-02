# Token-Importance-Application-Code
This is an application for analyzing the importance of individual tokens in prompts using various techniques like token visualization, cosine similarity, and SHAP values.

## Requirements:
- Python 3.7 or higher
- OpenAI API key and some credit
- These instructions are for Linux

## Installation and Setup
1. Download and unzip the folder
2. do ls and you should be able to see
```
$ ls
app.py features main.py requirements.txt utils
CustomSet.txt frames README.md storage
```
3. create a python virtual environment
```
python3 -m venv venv
```
4. activate the virtual envirnment using:
```
source venv/bin/activate
```
5. Install the requirements using:
```
pip install -r requirements.txt
```
6. Run the application:
```
python3 main.py
```

## Custom Prompts

The application uses prompts from a file named `CustomSet.txt`. You can edit this file to add your own prompts. 
