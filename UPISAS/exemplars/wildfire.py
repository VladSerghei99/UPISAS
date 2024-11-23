import pprint, time
from UPISAS.exemplar import Exemplar
import logging

pp = pprint.PrettyPrinter(indent=4)
logging.getLogger().setLevel(logging.INFO)


class Wildfire(Exemplar):
    """
    A class which encapsulates a self-adaptive exemplar run in a docker container.
    """
    _container_name = ""

    def __init__(self, auto_start: "Whether to immediately start the container after creation" = False,
                 container_name="Wildfire-UAVSimContainer"
                 ):
        '''Create an instance of the wildfire exemplar'''
        wildfire_docker_kwargs = {
            "name": container_name,
            "image": "wildfire-uvasim-image:latest",
            "ports": {55555: 55555, 8521: 8521}}

        super().__init__("http://localhost:55555", wildfire_docker_kwargs, auto_start)

    def start_run(self):
        if self.exemplar_container.status != "running":
            self.exemplar_container.start()

        self.exemplar_container.exec_run(cmd = f' sh -c "cd /usr/src/app && node" ', detach=True)