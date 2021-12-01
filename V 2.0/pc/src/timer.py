from PySide6 import QtCore
from time import sleep, time

# count-up timer to run in a thread
class Timer(QtCore.QRunnable):
    def __init__(self, updateTimer):
        super().__init__()
        self.running = True
        self.updateTimer = updateTimer # function from TrackingModel
        
        # for inserting new data
        self.robot_name = None
        self.index = None

        # for tracking robots with timer running
        self.racing_robots = {} # {"name1": [time, start_time], ..}
        self.index_list = []     # [i1, i2, i3, ..]

    @QtCore.Slot()
    # main thread loop
    def run(self):
        while self.running:
            # Update times every 0.01 seconds
            sleep(0.01)
            self.countTime(self.robot_name, self.index)
    
    # adding new robots & counting up time
    def countTime(self, robot_name=None, index=None):
        if robot_name is not None:
            if robot_name not in self.racing_robots:
                # add new robot to dict if not already racing
                self.racing_robots[robot_name] = [0, time()] # start time count from 0, get start_time
                self.robot_name = None

        for key in self.racing_robots:
            start_time = self.racing_robots[key][1]
            self.racing_robots[key][0] = (time()-start_time) * 1000 # elapsed time in ms

        if index is not None:
            self.index_list.append(index)
            self.index = None
            
        self.updateTimer(self.racing_robots, self.index_list)
    
    # fix all indexes when row removed
    def fixIndexes(self, start_index):
        for i, val in enumerate(self.index_list):
            if start_index < val:
                self.index_list[i] -= 1
    
    # inputting new robot_name, index to start its timer
    def inputData(self, robot_name, index):
        self.robot_name = robot_name
        self.index = index
    
    # remove robot_name from timer
    def stopCount(self, robot_name):
        i = list(self.racing_robots).index(robot_name)
        self.racing_robots.pop(robot_name)
        self.index_list.pop(i)

    # stop running thread
    def stop(self):
        self.robot_name = None
        self.index = None
        self.racing_robots = {}
        self.index_list = []
        self.running = False

