To run the simulation, there are two ways :-

1) Easier way -

Step 1 - Download the zip file folder T20_sim_S01_exe
Step 2 - Extract all
Step 3 - Run (Double - click) SIMULATION_exe exe/application file from the folder

For subsequent running of sim, just run SIMULATION_exe like any other application.

2) More efficient way - With python

Running it for first time,

Step 1 - Install python
Step 2 - Download the zip file folder T20_sim_S01
Step 3 - Extract all
Step 4 - Open the folder where you have extracted the file
Step 5 - Type 'cmd' in the location bar of the file manager (a command prompt window opens)
Step 6 - Connect to internet
Step 7 - Type 'python -m pip install ortools' 
		if it shows error try
		'py -m pip install ortools' or 'py -3 -m pip install ortools'
After it is done installing,
Step 8 - Type 'python -m pip install pandas' 
		if it shows error try
		'py -m pip install pandas' or 'py -3 -m pip install pandas'
After it is done installing,
Step 9 - Type 'SIMULATION.py'

That should start the sim.

After first time, just do Step 4, Step 5 and Step 9 to run it

##### ------ #####

CONDITIONS -

There are 3 settings for changing the pitch conditions, namely, 1)pace 2)spin 3)flatness

pace factors the probability of getting a wicket by a fast bowler.
Higher the pace setting, more chance of fast bowlers getting a wkt, medium bowlers also get little assist.
But note pace and spin doesnt hav direct impact on economy.

Spin same as pace, factors the probability of getting a wicket by a spin bowler
partspin bowlers get around half of the impact it has on spin bowler.

Flat settings impact the boundaries 4s, 6s of the series.
Higher the flat setting, more chance of 4s, 6s and lower it is less chance of 4s, 6s
This directly impacts the scoring rate and team score.

#### ----- #####

Once series is done, check seriesStats folder for all stats and scorecards and summary of each game
