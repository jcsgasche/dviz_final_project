# PFIFA! (Personal Functional Interactive Fitness Analysis)

# About
This is an interactive fitness dashboard which displays your personal progress to your needs.
The data is gathered through garmin fitness watches and is displayed with plotly and dash.

# Setup / Requirements
## Python Installation
To run this dashboard you need a running python installation on your OS. You can get python here: https://www.python.org/downloads/
## Python environment
We strongly encourage you to use a virtual environment for this app to keep dependencies seperate from any other project. Here's a guide on virtual environments: https://realpython.com/python-virtual-environments-a-primer/
## Python Packages
Please install the python packages from the requirements so that you can run the app. To do so, just run this command in the project root:
```bash
pip install -r ./requirements
```

# Running The App
Once everything is set up and the dependencies are resolved, you can run the app by just running `app.py` with python.
E.g. you can run this in project root, ideally in a dedicated python environment:
```bash
python3 ./src/app.py
```
Please run `app.py` from the project root (like in the snippet), for the paths to be correctly selected.

# App Usage
The app consists of four sections: "Load Data" and the three Visualisations "Muscle Activity Map", "Goal/Reached Dashboard" and "Activity Type Breakdown".
## Load Data
### Fetch from Garmin
You can load your personal fitness data through the Garmin API using your garmin account. Just enter your login credentials and fetch data straight through the API. 
Since the API usage is limited to regulate Garmin API traffic, therefore the data stays consistently on the page. 
You can download your data through the download button. This can be helpful for future cases if you want to use data on other devices when the API is not reachable or if you want to minimize API usage.
### Upload Local Dataset
In the "Upload Local Dataset" section you upload data you have previously downloaded from the fetching section.
## Toggle Colorblind Mode
For colorblind people to have a clear coloring scheme, there is a floating window with a toggle button to switch to colorblind friendly mode. We think the coloring is less intuitive since there are not all the colors available, but it is clearly distinguishable and the best solution for colorblind people.
## Set Time Range
Below the window with the Colorblind Switch, there is a window to set the time range. You can set any time range and the visualisations will update dynamically. If there is no data available in this period of time, it will be displayed in text in the visualisation.

# Visualisations
## Muscle Activity Map
This visualisation consist of two parts: a muscle map and a spider chart.
### Muscle Map
The Muscle Map shows how much you trained your primary and secondary muscles. Primary muscles are colored red (or blue for colorblind) and secondary muscles are colored yellow (or turquoise
for colorblind). For both primary and secondary muscles, the opacity of coloring shows how much a specific muscle group has been trained, where higher opacity stands for more training.
### Spider Chart
The Spider Chart is an additional visualisation next to the muscle map to complement it. It shows the balance of your training in a different way, as a spider chart. It allows you to analyze the balance of your strength training more directly.
## Goal/Reached Dashboard
The Goal/Reached Dashboard allows you to set goals for all kinds of metrics measure by your Garmin watch. There are two views: Summary View and Single Metric View, and a table to set goals for each metric.
### Summary View
In the Summary View you can see a comparison of your metrics summarized in a single bar each. You can either show all the metric or just show a selected view using the Custom Selection button.
### Single Metric View
The Single Metric View allows you to look at a single metric over time. It shows you each single training in the selected period of time and if they have individually reached the goal. You can set your goal for the single metric in this section.
### Metric Selection Table
To use the Metric Selection Table, you need to unfold it. You can set the goals for you metrics there (this also affects the single metrics goals).
## Activity Type Breakdown
In the Activity Type Breakdown you can see how your different types of training are balanced in a pie chart. You can set different metrics of measurements like duration or activities.