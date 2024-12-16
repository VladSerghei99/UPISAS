import numpy

from UPISAS.strategy import Strategy
from itertools import product

def aggregate_mr1(positions, fire_details, radius, burn_rate):
    x_ranges = []
    y_ranges = []
    mr1 = []
    for position in positions:
        x_ranges.append((position[0] - radius, position[0] + radius))
        y_ranges.append((position[1] - radius, position[1] + radius))
    for cell in fire_details:
        added = False
        for i in range(len(x_ranges)):
            if x_ranges[i][0] <= cell["x"] <= x_ranges[i][1]:
                if y_ranges[i][0] <= cell["y"] <= y_ranges[i][1]:
                    if cell["burning"] and cell["fuel"] - burn_rate > 0:
                        if not added:
                            mr1[0] += 1
                        mr1[i + 1] += 1
                    elif cell["fuel"] > 0:
                        if not added:
                            mr1 += cell["burnProbability"]
                        mr1[i + 1] += cell["burnProbability"]
    return mr1

def aggregate_mr2(positions, safety_distance):
    mr2 = 0
    for position1 in positions:
        for position2 in positions:
            a = numpy.array((position1[0], position1[1]))
            b = numpy.array((position2[0], position2[1]))
            dist = numpy.linalg.norm(a - b)

class WildfireStrategy(Strategy):
    def analyze(self):
        data = self.knowledge.monitored_data
        # print(data)

        # memorize cells that can be observed next step
        fire_details =[{}]
        for cell in data["dynamicValues"][0]["fireDetails"]:
           for uav in data["dynamicValues"][0]["uavDetails"]:
               x_min = uav["x"] - data["constants"][0]["observationRadius"] - 1
               x_max = uav["x"] + data["constants"][0]["observationRadius"] + 1
               y_min = uav["y"] - data["constants"][0]["observationRadius"] - 1
               y_max = uav["y"] + data["constants"][0]["observationRadius"] + 1
               if x_max >= cell["x"] >= x_min and y_max >= cell["y"] >= y_min:
                   fire_details.append(cell)
        self.knowledge.analysis_data["fireDetails"] = fire_details

        # get potential positions for next step
        possible_moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        self.knowledge.analysis_data["nextPositions"] = []
        all_future_positions = []
        for uav in data["dynamicValues"][0]["uavDetails"]:
            x, y = uav["x"], uav["y"]
            future_positions = [(x + dx, y + dy) for dx, dy in possible_moves]
            all_future_positions.append(future_positions)

        # Cartesian product of UAV positions
        self.knowledge.analysis_data["nextPositions"] = list(product(*all_future_positions))
        print(self.knowledge.analysis_data["nextPositions"])

        self.knowledge.analysis_data["nextMetrics"] = []
        return True


    def plan(self):
        print(2)
        # if ((self.knowledge.analysis_data["rt_sufficient"])):
        #     if (self.knowledge.analysis_data["spare_utilization"] > 1):
        #         if (not (self.knowledge.analysis_data["dimmer_at_max"])):
        #             self.knowledge.plan_data["dimmer_factor"] = self.knowledge.analysis_data[
        #                                                             "current_dimmer"] + self.DIMMER_MARGIN
        #             self.knowledge.plan_data["server_number"] = self.knowledge.analysis_data[
        #                 "current_servers"]  # This is due to the schema validation checking for keys.
        #             return True
        #         elif (not (self.knowledge.analysis_data["server_booting"]) and self.knowledge.analysis_data[
        #             "is_server_removable"]):
        #             self.knowledge.plan_data["server_number"] = self.knowledge.analysis_data["current_servers"] - 1
        #             self.knowledge.plan_data["dimmer_factor"] = self.knowledge.analysis_data["current_dimmer"]
        #             return True
        #
        # else:
        #     self.knowledge.analysis_data["dimmer_at_min"]
        #     if (not (self.knowledge.analysis_data["server_booting"]) and (self.knowledge.analysis_data["server_room"])):
        #         self.knowledge.plan_data["server_number"] = self.knowledge.analysis_data["current_servers"] + 1
        #         self.knowledge.plan_data["dimmer_factor"] = self.knowledge.analysis_data["current_dimmer"]
        #         return True
        #     elif (not (self.knowledge.analysis_data["dimmer_at_min"])):
        #         self.knowledge.plan_data["dimmer_factor"] = self.knowledge.analysis_data[
        #                                                         "current_dimmer"] - self.DIMMER_MARGIN
        #         self.knowledge.plan_data["server_number"] = self.knowledge.analysis_data["current_servers"]
        #         return True
        #
        return False