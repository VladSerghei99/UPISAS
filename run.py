from UPISAS.exemplars.wildfire import Wildfire
from UPISAS.strategies.wildfire_strategy import WildfireStrategy
import sys
import time

if __name__ == '__main__':
    
    exemplar = Wildfire(auto_start=True)
    time.sleep(3)
    exemplar.start_run()
    time.sleep(3)

    try:
        strategy = WildfireStrategy(exemplar)

        strategy.get_monitor_schema()
        strategy.get_adaptation_options_schema()
        strategy.get_execute_schema()

        for i in range(50):
            # input("Try to adapt?")
            strategy.monitor(verbose=False)
            strategy.analyze()
            print(strategy.knowledge.analysis_data["mr1"][1])
            print(strategy.knowledge.analysis_data["mr2"][1])
            strategy.plan()
            strategy.execute()
            
    except (Exception, KeyboardInterrupt) as e:
        print(str(e))
        input("something went wrong")
        exemplar.stop_container()
        sys.exit(0)