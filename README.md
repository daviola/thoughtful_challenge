# Thoughtful Take-Home project
This is a scrapper that should get data from [www.nytimes.com](www.nytimes.com) and store the images and text in the folder results

## Setting up the environment:

> Make sure you have python 3.11 or higher installed

> Make sure you have the chromedriver installed and matching your chrome version

Create the environment
```
python3 -m venv venv
```
Activate the environment:
```
source venv/bin/activate
```
Install de dependencies:
```
pip install -r requirements.txt
```
## Changing the configurations
You can access the configurations in config.ini but the scrapper should work fine with the default parameters

## Running the scrapper
Just run the main.py file

## Accessing results and logs
You can see the results in [excel](/results/excel/) and [img](results/img) folders inside [results/](results/)
You can see the logs in /logs folder


### Final considerations
I did not include pagination handling for the news results due to the timeframe, but is something that should be included in a real project