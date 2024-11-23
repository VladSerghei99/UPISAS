from UPISAS.strategy import Strategy

class BaselineStrategy(Strategy):

    def analyze(self):
        """
        Analyze the current state and determine UAV directions based on wind or dynamic fallback.
        """
        try:
            # Retrieve monitored data
            data = self.knowledge.monitored_data
            constants = data["constants"][0]
            dynamic_values = data["dynamicValues"][0]

            uav_details = dynamic_values["uavDetails"]

            self.knowledge.analysis_data["uav_directions"] = {}

            # Handle wind conditions
            if constants["activateWind"]:
                if constants["fixedWind"]:
                    # Single-direction wind
                    wind_direction = constants.get("windDirection", None)
                    if not wind_direction:
                        raise ValueError("Missing 'windDirection' for fixed wind.")
                    wind_dir_int = self.map_wind_direction_to_int(wind_direction)
                    for uav in uav_details:
                        self.knowledge.analysis_data["uav_directions"][uav["id"]] = wind_dir_int
                else:
                    # Multi-directional wind
                    first_direction = constants.get("firstDirection", None)
                    second_direction = constants.get("secondDirection", None)
                    first_dir_prob = constants.get("firstDirStrength", None)

                    if not (first_direction and second_direction and first_dir_prob):
                        raise ValueError("Multi-directional wind parameters missing.")

                    first_dir_int = self.map_wind_direction_to_int(first_direction)
                    second_dir_int = self.map_wind_direction_to_int(second_direction)

                    for i, uav in enumerate(uav_details):
                        if i < len(uav_details) * first_dir_prob:
                            self.knowledge.analysis_data["uav_directions"][
                                uav["id"]] = first_dir_int
                        else:
                            self.knowledge.analysis_data["uav_directions"][
                                uav["id"]] = second_dir_int
            else:
                # Sequential fallback
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
        """
        try:
            # Retrieve analyzed data
            analyzed_directions = self.knowledge.analysis_data["uav_directions"]

            # Create the plan data
            self.knowledge.plan_data["uavDetails"] = [
                {"id": uav_id, "direction": self.map_int_to_direction(direction)}
                for uav_id, direction in analyzed_directions.items()
            ]

            return True
        except KeyError as e:
            print(f"[Planning Error] KeyError: {e}")
            return False
        except Exception as e:
            print(f"[Planning Error] Unexpected error: {e}")
            return False

    @staticmethod
    def map_wind_direction_to_int(wind_direction):
        """
        Map wind direction to integer values as per schema.
        """
        mapping = {
            "north": 0,
            "east": 1,
            "south": 2,
            "west": 3,
        }
        return mapping.get(wind_direction, 0)  # Default to 0 (north) if wind direction is invalid

    @staticmethod
    def map_int_to_direction(direction):
        """
        Map integer values to direction strings as per execute schema.
        """
        mapping = {
            0: "up",
            1: "right",
            2: "down",
            3: "left",
        }
        return mapping.get(direction, "up")  # Default to "up" if direction is invalid
