import numpy

from UPISAS.strategy import Strategy
from itertools import product

def aggregate_mr1(uav_positions, fire_details, radius, burn_rate):
    """
    Calculate utility of the total area observed by the set of UAVs as well
    as for each one separately

    Returns:
        mr1_total(float): Utility of the total area observed by the UAVs
        mr1(list(float)): Utility value of area observed by each UAV
    """

    x_ranges = []
    y_ranges = []
    mr1_total = 0
    mr1 = [0] * len(uav_positions)
    # Calculate area of coverage of UAVs
    for position in uav_positions:
        x_ranges.append((position[0] - radius, position[0] + radius))
        y_ranges.append((position[1] - radius, position[1] + radius))

    # For each covered cell add its utility value to the sum, 1 if burning, probability of burning otherwise
    for cell in fire_details:
        added = False
        for i in range(len(x_ranges)):
            if x_ranges[i][0] <= cell["x"] <= x_ranges[i][1]:
                if y_ranges[i][0] <= cell["y"] <= y_ranges[i][1]:
                    if cell["burning"] and cell["fuel"] - burn_rate > 0 and not cell["smoke"]:
                        if not added:
                            mr1_total += 1
                            added = True
                        mr1[i] += 1
                    elif cell["fuel"] > 0 and not cell["smoke"]:
                        if not added:
                            mr1_total += cell["burnProbability"]
                            added = True

    return mr1_total, mr1

def aggregate_mr2(positions, safety_distance):
    """
    Calculate safety risks for the UAVs

    Returns:
        mr2_distance(float): Sum of differences between safety distance and
        distances between UAVs
        mr2(int): Safety risk of the UAVs
    """
    mr2 = 0
    mr2_distance = 0
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            a = numpy.array((positions[i][0], positions[i][1]))
            b = numpy.array((positions[j][0], positions[j][1]))
            dist = float(numpy.linalg.norm(a - b))
            if dist < safety_distance:
                mr2_distance += (safety_distance - dist)
                mr2 += 1
    return mr2_distance, mr2

class WildfireStrategy(Strategy):

    def analyze(self):
        """
        Analyze the current state and determine associated scores for possible future positions
        of the UAVs for the next step

        Returns:
            True
        """
        data = self.knowledge.monitored_data
        self.knowledge.analysis_data = {}

        # memorize the set of cells that can be observed next step
        fire_details = []
        x_min = data["constants"][0]["width"]
        y_min = data["constants"][0]["height"]
        x_max = 0
        y_max = 0
        for uav in data["dynamicValues"][0]["uavDetails"]:
            x_min = min(uav["x"] - data["constants"][0]["observationRadius"] - 1, x_min)
            x_max = max(uav["x"] + data["constants"][0]["observationRadius"] + 1, x_max)
            y_min = min(uav["y"] - data["constants"][0]["observationRadius"] - 1, y_min)
            y_max = max(uav["y"] + data["constants"][0]["observationRadius"] + 1, y_max)
        for cell in data["dynamicValues"][0]["fireDetails"]:
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

        # calculate cartesian product of UAV positions to generate all possible position combinations
        self.knowledge.analysis_data["nextPositions"] = list(product(*all_future_positions))

        self.knowledge.analysis_data["nextMetrics"] = []

        # calculate the metrics for all possible future positions
        for position_combination in self.knowledge.analysis_data["nextPositions"]:
            mr1 = aggregate_mr1(position_combination, fire_details, data["constants"][0]["observationRadius"],
                                data["constants"][0]["burningRate"])
            mr2 = aggregate_mr2(position_combination, data["constants"][0]["securityDistance"])
            self.knowledge.analysis_data["nextMetrics"].append((mr1[0], mr2[0]))
            self.knowledge.analysis_data["mr1"] = mr1
            self.knowledge.analysis_data["mr2"] = mr2
        return True


    def plan(self):
        """
        Determine which combination of future positions should be used, comparing by the defined metrics

        Returns:
            True
        """
        positions = self.knowledge.analysis_data["nextPositions"]
        metrics = self.knowledge.analysis_data["nextMetrics"]
        uavs = self.knowledge.monitored_data["dynamicValues"][0]["uavDetails"]

        # calculate which combination has the best utility value, first by mr2 then by mr1 to differentiate
        # between equal mr2 values
        best_dir_index = min(
            range(len(metrics)),
            key=lambda j: (
                metrics[j][1],
                -metrics[j][0]
            )
        )

        # determine new directions for each UAV
        next_positions = positions[best_dir_index]
        self.knowledge.plan_data["uavDetails"] = []
        for i in range(len(uavs)):
            uav_id = uavs[i]["id"]

            if next_positions[i][0] == uavs[i]["x"]:
                if next_positions[i][1] > uavs[i]["y"]:
                    next_dir = 0
                else:
                    next_dir = 2
            elif next_positions[i][0] > uavs[i]["x"]:
                next_dir = 1
            else:
                next_dir = 3

            self.knowledge.plan_data["uavDetails"].append({
                "id": uav_id,
                "direction": next_dir
            })

        return True