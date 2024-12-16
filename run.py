from UPISAS.exemplars.swim import SWIM
from UPISAS.exemplars.wildfire import Wildfire
from UPISAS.strategies.swim_reactive_strategy import ReactiveAdaptationManager
from UPISAS.strategies.wildfire_strategy import WildfireStrategy
from UPISAS.exemplar import Exemplar
from UPISAS.strategies.baseline_strategy import BaselineStrategy
import signal
import sys
import time

if __name__ == '__main__':
    
    exemplar = Wildfire(auto_start=True)
    time.sleep(3)
    exemplar.start_run()
    time.sleep(3)

    try:
        strategy = BaselineStrategy(exemplar)

        strategy.get_monitor_schema()
        strategy.get_adaptation_options_schema()
        strategy.get_execute_schema()

        while True:
            input("Try to adapt?")
            strategy.monitor(verbose=False)
            if strategy.analyze():
                if strategy.plan():
                    strategy.execute()
            
    except (Exception, KeyboardInterrupt) as e:
        print(str(e))
        input("something went wrong")
        exemplar.stop_container()
        sys.exit(0)