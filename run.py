from UPISAS.exemplars.wildfire import Wildfire
from UPISAS.strategies.wildfire_strategy import WildfireStrategy
import matplotlib.pyplot as plt
import sys
import time

if __name__ == '__main__':
    
    exemplar = Wildfire(auto_start=True)
    time.sleep(3)
    exemplar.start_run()
    time.sleep(3)
    mr1_history = []
    mr2_history = []
    mr1a_history = []

    try:
        strategy = WildfireStrategy(exemplar)

        strategy.get_monitor_schema()
        strategy.get_adaptation_options_schema()
        strategy.get_execute_schema()
        num_steps = 35
        for i in range(num_steps):
            # input("Try to adapt?")
            strategy.monitor(verbose=False)
            strategy.analyze()
            mr1_history.append(strategy.knowledge.analysis_data["mr1"])
            mr2_history.append(strategy.knowledge.analysis_data["mr2"])
            mr1a_history.append(strategy.knowledge.analysis_data["mr1a"])
            strategy.plan()
            strategy.execute()
        fig, ax = plt.subplots(2, 1, figsize=(8, 6))

        #subplot for aggregate mr1
        ax[0].plot(range(num_steps), mr1a_history, label="Overall coverage", color='black', marker='o')
        ax[0].legend()
        ax[0].set_title("Total UAV coverage over time")
        ax[0].set_xlabel("Time step")
        ax[0].set_ylabel("Value")

        # Subplot for mr1
        ax[1].plot(range(num_steps), [v[0] for v in mr1_history], label="UAV1", color='blue', marker='o')
        ax[1].plot(range(num_steps), [v[1] for v in mr1_history], label="UAV2", color='orange', marker='o')
        ax[1].plot(range(num_steps), [v[2] for v in mr1_history], label="UAV3", color='green', marker='o')
        ax[1].legend()
        ax[1].set_title("MR1 over time")
        ax[1].set_xlabel("Time step")
        ax[1].set_ylabel("Value")

        # Subplot for mr2
        ax[2].plot(range(num_steps), mr2_history, label="MR2", color='red', marker='o')
        ax[2].legend()
        ax[2].set_title("MR2 over time")
        ax[2].set_xlabel("Time step")
        ax[2].set_ylabel("Value")

        # Adjust layout for better spacing
        plt.tight_layout()

        # Save the plot as an image
        plt.savefig('evolution_plot.png')

        # Show the plot
        plt.show()
    except (Exception, KeyboardInterrupt) as e:
        print(str(e))
        input("something went wrong")
        exemplar.stop_container()
        sys.exit(0)