class Tracking:
    """Class to track information about individual robots on the track"""

    def __init__(self, name):
        self.name = name
        self.lap_times = {}
        self.lap_id = 1

    def changeName(self, new_name):
        self.name = new_name

    def addTime(self, time_ms):
        self.lap_times[self.lap_id] = time_ms
        self.lap_id += 1

    def removeTime(self, time_id):
        if time_id in self.lap_times.keys():
            self.lap_times.pop(time_id)

    def printData(self):
        print("Name of robot:", self.name)
        if not self.lap_times:  # empty list is False
            print("No lap times have been added.")
        else:
            # a = sorted(self.lap_times.items(), key=lambda x: x[1]) # SORTS TIMES IN ASCENDING ORDER (FASTEST TIMES FIRST)
            for key, value in self.lap_times.items():
                print(key, ") ", value, "ms")

    def getData(self):
        return {"robot_name": self.name, "lap_times": self.lap_times}


""" TRACKING TESTING """
robot1 = Tracking("Terminaator")
robot1.addTime(77123)
robot1.addTime(82000)
robot1.addTime(44555)
robot1.addTime(65234)
robot1.removeTime(2)
robot1.removeTime(7)

robot2 = Tracking("ERROR")
robot2.changeName("WALL-E")

robots = [robot1, robot2]
for robot in robots:
    robot.printData()
    print("")

print(f"\n\nDATA: {robot1.getData()}")
""" TESTING END """
