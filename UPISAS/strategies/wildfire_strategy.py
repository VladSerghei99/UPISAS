from UPISAS.strategy import Strategy


class WildfireStrategy(Strategy):
    def analyze(self):
        data = self.knowledge.monitored_data
        print(data)
        self.knowledge.analysis_data["MR1"] = data["MR1"]
        self.knowledge.analysis_data["MR2"] = data["MR2"]
        # for each UAV calculate local MR1 for each direction
        return True
        #
        # return False

    def plan(self):
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