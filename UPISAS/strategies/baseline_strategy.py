from UPISAS.strategy import Strategy
import numpy


class BaselineStrategy(Strategy):

    def analyze(self):
        """
        Analyze the current state and calculate MR1 and MR2 based on UAV positions and fire details.
        Returns:
            True if analysis was successful, False otherwise.
        """
        try:
            # Retrieve monitored data
            data = self.knowledge.monitored_data
            self.knowledge.analysis_data = {}

            constants = data["constants"][0]
            dynamic_values = data["dynamicValues"][0]

            fire_details = dynamic_values.get("fireDetails", [])
            uav_details = dynamic_values["uavDetails"]

            observation_radius = constants["observationRadius"]
            burn_rate = constants["burningRate"]
            safety_distance = constants["securityDistance"]

            uav_positions = [(uav["x"], uav["y"]) for uav in uav_details]
            print(f"[Analysis] UAV positions: {uav_positions}")

            # Calculate MR1 and MR2
            _, mr1_per_uav, _ = self.aggregate_mr1(uav_positions, fire_details,
                                                   observation_radius,
                                                   burn_rate)
            mr2_risk, _ = self.aggregate_mr2(uav_positions, safety_distance)

            self.knowledge.analysis_data["mr1"] = mr1_per_uav
            self.knowledge.analysis_data["mr2"] = mr2_risk

            # Analyze UAV directions based on wind
            self.knowledge.analysis_data["uav_directions"] = {}
            if constants["activateWind"]:
                if constants["fixedWind"]:
                    wind_dir_int = {"east": 0, "west": 2, "south": 1, "north": 3}.get(constants[
                                                                                       "windDirection"], 0)
                    for uav in uav_details:
                        self.knowledge.analysis_data["uav_directions"][uav["id"]] = wind_dir_int
                        print(f"UAV {uav['id']} direction: {wind_dir_int}")
                else:
                    # Multi-directional wind
                    first_dir_prob = constants.get("firstDirStrength", 0.5)
                    num_first_dir = int(len(uav_details) * first_dir_prob)
                    for i, uav in enumerate(uav_details):
                        self.knowledge.analysis_data["uav_directions"][uav["id"]] = 0 if i < num_first_dir else 2
            else:
                # Sequential fallback
                directions = [0, 1, 2, 3]
                for i, uav in enumerate(uav_details):
                    self.knowledge.analysis_data["uav_directions"][uav["id"]] = directions[i % len(directions)]

            self.knowledge.analysis_data["mr1a"] = self.aggregate_mr1(uav_positions,
                                                                     fire_details,
                                                                 data["constants"][0][
                                                                     "observationRadius"],
                                                                 data["constants"][0][
                                                                     "burningRate"])[2]
            MR1a = self.knowledge.analysis_data["mr1a"]

            print(f"[Analysis] MR1: {mr1_per_uav}, MR2: {mr2_risk}, MR1a: {MR1a}")
            return True
        except Exception as e:
            print(f"[Analysis Error] {e}")
            return False

    def plan(self):
        """
        Plan UAV movements based on analyzed directions.
        Returns:
            True if planning was successful, False otherwise.
        """
        try:
            # Retrieve analyzed directions and current UAV details
            analyzed_directions = self.knowledge.analysis_data["uav_directions"]
            monitored_data = self.knowledge.monitored_data["dynamicValues"][0]
            current_uav_details = monitored_data["uavDetails"]

            self.knowledge.plan_data["uavDetails"] = []
            for uav in current_uav_details:
                uav_id = uav["id"]
                direction = analyzed_directions[uav_id]

                # Append UAV details for execution
                self.knowledge.plan_data["uavDetails"].append({
                    "id": uav_id,
                    "direction": direction,
                })

            print(f"[Plan] Planned UAV movements: {self.knowledge.plan_data}")
            return True
        except Exception as e:
            print(f"[Planning Error] {e}")
            return False

    @staticmethod
    def aggregate_mr1(uav_positions, fire_details, radius, burn_rate):
        x_ranges = []
        y_ranges = []
        mr1_total = 0
        mr1a = 0
        mr1 = [0] * len(uav_positions)

        # Calculate area of coverage of UAVs
        for position in uav_positions:
            x_ranges.append((position[0] - radius, position[0] + radius))
            y_ranges.append((position[1] - radius, position[1] + radius))

        # For each covered cell add its utility value
        for cell in fire_details:
            added = False
            for i in range(len(x_ranges)):
                if x_ranges[i][0] <= cell["x"] <= x_ranges[i][1]:
                    if y_ranges[i][0] <= cell["y"] <= y_ranges[i][1]:
                        if cell["burning"] and cell["fuel"] - burn_rate > 0 and not cell["smoke"]:
                            if not added:
                                mr1_total += 1
                                mr1a += 1
                                added = True
                            mr1[i] += 1
                        elif cell["fuel"] > 0 and not cell["smoke"]:
                            if not added:
                                mr1_total += cell["burnProbability"]
                                added = True

        return mr1_total, mr1, mr1a

    @staticmethod
    def aggregate_mr2(positions, safety_distance):
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
        return mr2, safety_distance
