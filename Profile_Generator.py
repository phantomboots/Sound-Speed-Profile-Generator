# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import tkinter as tk
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog as fd
import re #Regular expressions module
from math import ceil
from tkinter import messagebox as mb

#Main window for the program
root = tk.Tk()

#Setup two frames, one for the buttons and text entry boxes, the second for the graph.
frame1 = tk.Frame(root)
frame2 = tk.Frame(root)

frame1.grid(row=0, column=0, pady=2, padx=2)
frame2.grid(row=0, column=1, pady=2, padx=2)
scroll = tk.Scrollbar(frame1)


#Dive Name, Time Entry Boxes and App Title

root.title("Sound Speed Profile Generator")

tips = tk.Label(frame1, text = "Enter the Dive Start and On Bottom time, as 'YYYY-MM-DD HH:MM:SS'").grid(row=0, columnspan=2, pady=20)
dive_name = tk.Label(frame1, text = "Dive Name").grid(row=1, sticky=tk.W)
start_label = tk.Label(frame1, text = "Dive Start Time").grid(row=2, sticky=tk.W)
end_label = tk.Label(frame1, text = "Dive End Time").grid(row=3, sticky=tk.W)
status_box = tk.Text(frame1, height = 20, width =50)


dive_enter = tk.Entry(frame1)
start_enter = tk.Entry(frame1)
end_enter = tk.Entry(frame1)


dive_enter.grid(row=1, column=1, sticky = tk.W)
start_enter.grid(row=2, column=1, sticky = tk.W)
end_enter.grid(row=3, column=1, sticky = tk.W)

#Set the size the multiline text box that displays program status, and activate the scrollbar feature for it.
status_box.grid(row=6, columnspan = 2)
scroll.config(orient="vertical", command=status_box.yview)
status_box.configure(yscrollcommand=scroll.set)
scroll.grid(row=6, column=3)

#Set a default value to the system time, to save some time. Add this as a default value to the text entry box. Set an
#end time of the system time  plus 20 mins (a reasonable time space to reach bottom after starting decsent)

now_time = datetime.now()
next_time = datetime.now() + timedelta(minutes = 20)
now_time = now_time.strftime("%Y-%m-%d %H:%M:%S")
next_time = next_time.strftime("%Y-%m-%d %H:%M:%S")

dive_enter.insert(0, "TestDive")
start_enter.insert(0, now_time) #The first argument, 0, means enter the string at index position 0.
end_enter.insert(0, next_time)

start = start_enter.get()
end = end_enter.get()

start_time = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
end_time = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")

#Initialize variables in global scope, to be used in functions below.

col_names = ["date_time", "Depth_m", "SoundVelocity_ms"]
full_log = pd.DataFrame(columns = col_names)  #Empty dataframe object, to hold the ASDL files that are read in. This will be converted to a dataframe.
descent = pd.DataFrame(columns = col_names) #Empty dataframe object, to hold the 'trimmed' data files that contain only the descent to target depth.

"""
A function to skip rows in the RBR logs that start with 'Ready", "meminfo", or "<COM" while reading in data files. The "<COM" 
portion should not be required, but is kept just to catch that potential error. The function remove the bad rows, then
extract the time, depth and sound velocity columns and saves them to a dictionary, before converting to a data frame object.

ASDL data logs from the SeaBird 25+ CTD don't suffer from this issue, but running the regular expression checks below has no detrimental
effects here, so best to just leave it in.

"""

def filter_logs(ASDL_file):   
    timeval = []
    depthval = []
    soundval = []
    readin = []
    logs = open(ASDL_file, encoding = "utf-8", errors = "ignore").readlines()
    for index, item in enumerate(logs):
        match = re.search("^\d{4}-\d{2}-\d{2}", logs[index])
        if match:
            readin = logs[index].split(",") #Split the good data by comma seperated values.
            timeval.append(readin[1])
            depthval.append(readin[2])
            soundval.append(readin[3])
    #Need to create a dictionary as an intermediate step before generating a DataFrame.       
    data = {"date_time": timeval, "Depth_m": depthval, "SoundVelocity_ms": soundval}
    df = pd.DataFrame(data)   
    return df


"""
Button for a file Open Dialog Window. This function will allow for opening of multiple files, in case the descent period
spans more than one ASDL log file (unlikely, but possible) Read in the selected DFs and merge them, then filter to
relevant columns, and coerce date_time to appropriate variable.

**An initial file path for the dialog box could be set by using the (initialdir =) argument

"""

#Empty list to hold data frames created from ASDL log files

    
def callback():
    global full_log   
    log_files = []
    name=fd.askopenfilenames(title = "Select ASDL Log Files...")
    for filename in name: 
        df = filter_logs(filename)
#        df = pd.read_csv(filename, usecols = [0,6,8] , names = ["date_time", "Depth_m", "SoundVelocity_ms"], skiprows = lambda x: skip_RBR(x))
        df["date_time"] = pd.to_datetime(df["date_time"], format = "%Y-%m-%d %H:%M:%S")
        df["Depth_m"] = pd.to_numeric(df["Depth_m"])
        df["SoundVelocity_ms"] = pd.to_numeric(df["SoundVelocity_ms"])
        log_files.append(df)  
        status_box.insert("end", str("Read in file " + filename + "\n" + " with " + str(len(df)) + " entries." + "\n"))
        status_box.see("end")
    full_log = pd.concat(log_files)    
    print(full_log)
    status_box.insert("end", str("Successfully created DataFrame with " + str(len(full_log)) + " entries." + "\n"))
    status_box.see("end")
    return full_log

    
errmsg = "Error!"
tk.Button(frame1, text = "Open File", command = callback).grid(row=4, column=0, sticky=tk.W, pady=10)

#Function to mask the dataframe to the date_time required, and then plot the masked DF (the 'descent' DF).
#This function is not called directly by a widget, but rather inside of enter_and_plot()
def mask_and_plot(df, mask_start, mask_end):
    global full_log, descent
    figure = plt.Figure(figsize=(6,5), dpi=100)
    ax = figure.add_subplot(111)
    ax.invert_yaxis()
    chart_type = FigureCanvasTkAgg(figure, frame2)
    chart_type.get_tk_widget().grid(row=0, column=0)
    mask = (full_log["date_time"] > mask_start) & (full_log["date_time"] <= mask_end)
    descent = full_log.loc[mask]
    status_box.insert("end", "Data filtered between " + str(mask_start) + " and \n" + str(mask_end) + " with " + str(len(descent)) + " entries." + "\n")
    status_box.see("end")
    descent.plot(kind="line", x="SoundVelocity_ms", y="Depth_m", legend = True, ax=ax)
    return descent

#Function and Button to "Set Times" and generate the chart

def enter_and_plot():
    global full_log, descent
    start = start_enter.get()
    end =  end_enter.get()
    start = datetime.strptime(start, "%Y-%m-%d %H:%M:%S") #Unsure if redundant, leave in for now.
    end = datetime.strptime(end, "%Y-%m-%d %H:%M:%S") #Unsure if redundant, leave in for now.    
    descent = mask_and_plot(full_log, start, end)
    return descent


tk.Button(frame1, text='Set Times and Graph', command=enter_and_plot).grid(row=4, column=1, sticky=tk.W, pady=10)

#A function to select the save directory
    
def savelocation():
    global save_dir
    save_dir = fd.askdirectory(title = "Select Sound Speed Profile Save Location...")
    status_box.insert("end", "Profile save directory set to \n" + save_dir + "\n")
    status_box.see("end")
    return save_dir

tk.Button(frame1, text='Select Save Directory', command=savelocation).grid(row=5, column=0, sticky=tk.W, pady=10)

#Button to Export the Data to a Sound Speed Profile. The if() statement checks to see if there is more than 
#1000 readings, which is the most that TrackMan can handle. If there is, it will slice the data frame to ensure that
#there are less than 1000 values in the export.

def make_profile():
    global descent
    dive = dive_enter.get()
    profile = descent[["Depth_m","SoundVelocity_ms"]]
    if len(profile) > 200:
        to_round = len(profile)/200
        to_round = ceil(to_round)
        slicing = list(range(0, len(profile), to_round))
        profile = profile.iloc[slicing]
    if dive == "TestDive":
        mb.showwarning(title="Check Dive Name", message="Did you forget to change the dive name?")
    profile.to_csv(str(save_dir + dive + ".csv"), index = False)
    status_box.insert("end","Saved profile to: \n" + save_dir + "/" + dive + ".csv \n\n")
    status_box.see("end")
    status_box.insert("end",profile)
    status_box.see("end")


tk.Button(frame1, text = "Export Sound Speed Profile", command=make_profile).grid(row=5, column = 1, sticky=tk.W, pady = 10)



root.mainloop()