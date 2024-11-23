from pathlib import Path
import time
from EventManager.Models.RunnerEvents import RunnerEvents
from EventManager.EventSubscriptionController import EventSubscriptionController
from ConfigValidator.Config.Models.RunTableModel import RunTableModel
from ConfigValidator.Config.Models.FactorModel import FactorModel
from ConfigValidator.Config.Models.RunnerContext import RunnerContext
from ConfigValidator.Config.Models.OperationType import OperationType
from ProgressManager.Output.OutputProcedure import OutputProcedure as output

from UPISAS.strategies.baseline_strategy import BaselineStrategy
from UPISAS.exemplars.wildfire import Wildfire


class RunnerConfig:
    ROOT_DIR = Path(__file__).parent

    # Experiment-specific attributes
    name: str = "wildfire_experiment"
    results_output_path: Path = ROOT_DIR / "experiments"
    operation_type: OperationType = OperationType.AUTO
    time_between_runs_in_ms: int = 1000
    run_table_model: RunTableModel = None  # Initialize as None

    def __init__(self):
        """Set up experiment-specific hooks."""
        self.exemplar = None
        self.strategy = None

        # Define event hooks for the experiment runner
        EventSubscriptionController.subscribe_to_multiple_events([
            (RunnerEvents.BEFORE_EXPERIMENT, self.before_experiment),
            (RunnerEvents.BEFORE_RUN, self.before_run),
            (RunnerEvents.START_RUN, self.start_run),
            (RunnerEvents.START_MEASUREMENT, self.start_measurement),
            (RunnerEvents.INTERACT, self.interact),
            (RunnerEvents.STOP_MEASUREMENT, self.stop_measurement),
            (RunnerEvents.STOP_RUN, self.stop_run),
            (RunnerEvents.POPULATE_RUN_DATA, self.populate_run_data),
            (RunnerEvents.AFTER_EXPERIMENT, self.after_experiment),
        ])

        self.run_table_model = self.create_run_table_model()  # Initialize run_table_model
        output.console_log("Wildfire RunnerConfig loaded")

    def create_run_table_model(self) -> RunTableModel:
        """Create and return the run table model."""
        factor1 = FactorModel("wind_direction", ["north", "south", "east", "west"])
        return RunTableModel(
            factors=[factor1],
            data_columns=["burned_area"]
        )

    def before_experiment(self) -> None:
        """Actions before the experiment."""
        output.console_log("Before Experiment Hook: Setting up Wildfire.")

    def before_run(self) -> None:
        """Prepare exemplar and strategy for each run."""
        self.exemplar = Wildfire(auto_start=True)
        self.strategy = BaselineStrategy(self.exemplar)

    def start_run(self, context: RunnerContext) -> None:
        """Start a new run with the specific configuration."""
        wind_direction = context.run_variation["wind_direction"]
        self.exemplar.set_wind_direction(wind_direction)
        self.exemplar.start_run()
        time.sleep(3)
        output.console_log(f"Started run with wind_direction = {wind_direction}")

    def start_measurement(self, context: RunnerContext) -> None:
        """Actions before measurements."""
        output.console_log("Starting measurement.")

    def interact(self, context: RunnerContext) -> None:
        """Interact with the exemplar."""
        for _ in range(5):
            self.strategy.monitor(verbose=True)
            if self.strategy.analyze():
                if self.strategy.plan():
                    self.strategy.execute()
            time.sleep(3)

    def stop_measurement(self, context: RunnerContext) -> None:
        """Actions to stop measurement."""
        output.console_log("Stopping measurement.")

    def stop_run(self, context: RunnerContext) -> None:
        """Cleanup after a run."""
        self.exemplar.stop_container()
        output.console_log("Run stopped.")

    def populate_run_data(self, context: RunnerContext):
        """Collect results."""
        monitored_data = self.strategy.knowledge.monitored_data
        burned_area = monitored_data.get("burned_area", 0)
        return {"burned_area": burned_area}

    def after_experiment(self) -> None:
        """Cleanup after the experiment."""
        output.console_log("Experiment completed.")
