from UPISAS.strategy import Strategy
import math


class BaselineStrategy(Strategy):

    def analyze(self):
        """
        Analyze the current state and determine UAV directions based on wind or dynamic fallback.

        Returns:
            True if analysis was successful, False otherwise.
        """
        try:
            # retrieve monitored data
            data = self.knowledge.monitored_data
            constants = data["constants"][0]
            dynamic_values = data["dynamicValues"][0]

            uav_details = dynamic_values["uavDetails"]

            self.knowledge.analysis_data["uav_directions"] = {}

            # handle wind conditions
            if constants["activateWind"]:
                if constants["fixedWind"]:
                    # single-direction wind
                    wind_direction = constants.get("windDirection", None)
                    if not wind_direction:
                        raise ValueError("Missing 'windDirection' for fixed wind.")
                    wind_dir_int = self.map_wind_direction_to_int(wind_direction)
                    for uav in uav_details:
                        self.knowledge.analysis_data["uav_directions"][uav["id"]] = wind_dir_int
                else:
                    # multi-directional wind
                    first_direction = constants.get("firstDirection", None)
                    second_direction = constants.get("secondDirection", None)
                    first_dir_prob = constants.get("firstDirStrength", None)

                    if not (first_direction and second_direction and first_dir_prob):
                        raise ValueError("Multi-directional wind parameters missing.")

                    first_dir_int = self.map_wind_direction_to_int(first_direction)
                    second_dir_int = self.map_wind_direction_to_int(second_direction)

                    num_first_dir = math.ceil(len(uav_details) * first_dir_prob)

                    # distribute UAVs based on the calculated counts
                    for i, uav in enumerate(uav_details):
                        if i < num_first_dir:
                            self.knowledge.analysis_data["uav_directions"][
                                uav["id"]] = first_dir_int
                        else:
                            self.knowledge.analysis_data["uav_directions"][
                                uav["id"]] = second_dir_int
            else:
                # sequential fallback if wind is not active
                directions = [0, 1, 2, 3]  # North, East, South, West
                for i, uav in enumerate(uav_details):
                    self.knowledge.analysis_data["uav_directions"][uav["id"]] = directions[
                        i % len(directions)]

            return True
        except ValueError as e:
            print(f"[Analysis Error] ValueError: {e}")
            return False
        except KeyError as e:
            print(f"[Analysis Error] KeyError: {e}")
            return False
        except Exception as e:
            print(f"[Analysis Error] Unexpected error: {e}")
            return False

    def plan(self):
        """
        Plan UAV movements based on the analyzed directions.

        Returns:
            True if planning was successful, False otherwise.
        """
        try:
            # retrieve analyzed directions
            analyzed_directions = self.knowledge.analysis_data["uav_directions"]

            # retrieve current UAV positions from monitored data
            monitored_data = self.knowledge.monitored_data["dynamicValues"][-1]
            current_uav_details = monitored_data["uavDetails"]

            self.knowledge.plan_data["uavDetails"] = []
            for uav in current_uav_details:
                uav_id = uav["id"]
                direction = analyzed_directions[uav_id]
                x, y = uav["x"], uav["y"]  # get current coordinates

                if direction == 0:  # north
                    y += 1
                elif direction == 1:  # east
                    x += 1
                elif direction == 2:  # south
                    y -= 1
                elif direction == 3:  # west
                    x -= 1

                # append the UAV details to the plan
                self.knowledge.plan_data["uavDetails"].append({
                    "id": uav_id,
                    "x": x,
                    "y": y,
                    "direction": self.map_int_to_direction(direction)
                })

            print(f"[Plan] Generated plan with UAV coordinates and directions: "
                f"{self.knowledge.plan_data}")
            return True
        except KeyError as e:
            print(f"[Planning Error] KeyError: {e}")
            return False
        except Exception as e:
            print(f"[Planning Error] Unexpected error: {e}")
            return False

    @staticmethod
    def map_wind_direction_to_int(wind_direction):
        """Map wind direction to integer values as per schema.

        Args:
            wind_direction (str): Wind direction string.

        Returns:
            int: Integer value mapped to wind direction.
        """
        mapping = {
            "north": 0,
            "east": 1,
            "south": 2,
            "west": 3,
        }
        return mapping.get(wind_direction, 0)

    @staticmethod
    def map_int_to_direction(direction):
        """Map integer values to direction strings as per execute schema.

        Args:
            direction (int): Integer value representing direction.

        Returns:
            str: Direction string mapped to integer value.
        """
        mapping = {
            0: "up",
            1: "right",
            2: "down",
            3: "left",
        }
        return mapping.get(direction, "up")
