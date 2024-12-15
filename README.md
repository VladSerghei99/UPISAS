# UPISAS
Unified Python interface for self-adaptive system exemplars.

### Prerequisites 
Tested with Python 3.9.12, should work with >=3.7.

### Installation
In a terminal, navigate to the parent folder of the project and issue:
```
pip install -r requirements.txt
```
### Run unit tests
In a terminal, navigate to the parent folder of the project and issue:
```
python -m UPISAS.tests.upisas.test_exemplar
python -m UPISAS.tests.upisas.test_strategy
python -m UPISAS.tests.swim.test_swim_interface
```
### Run
In a terminal, navigate to the parent folder of the project and issue:
```
python run.py
```

### Using experiment runner 
**Please be advised**, experiment runner does not work on native Windows. Since UPISAS also uses docker, your Windows system should have the Windows Subsystem for Linux (WSL) installed already. You can then simply use Python within the WSL for both UPISAS and Experiment Runner (restart the installation above from scratch there, and then proceed with the below).
```
cd experiment-runner
git submodule update --init --recursive
pip install -r requirements.txt
cd ..
sh run.sh 
```

### Changes to the Wildfire codebase
These are the modifications I made to the original Wildfire code to make it work with UPISAS:

In the `api.py` file, I changed the following line:
```python
values.NUM_AGENTS = 3
```
to
```python
values.NUM_AGENTS = values.NUM_AGENTS
```
 and in the `common_fiexed_variables.py` file, I added the following lines:
```python
FIRST_DIR = 'north'
SECOND_DIR = 'west'
FIRST_DIR_PROB = 0.5
```
because they were not declared until `WIND_DIRECTION` was False.

The `Docker` file has also been changed into the following:
```dockerfile
WORKDIR /code

RUN apt update

RUN apt upgrade

RUN apt install -y python3 python3-pip

RUN pip install jsonschema networkx numpy matplotlib flask
RUN pip install mesa==1.2.1

RUN pip install "mesa [viz]"

CMD ["python3", "/code/wildfire/api.py"]
```

### Running the experiment with UPISAS

I use the following commands when running the Wildifre experiment with UPISAS:

In the Wildfire folder I run
``` shell
make runFirst
```
to start the experiment. 

Then in the UPISAS folder I run
``` shell
python run.py
```
to start the UPISAS experiment. This is the place where I get the along when choosing to adapt.

These are all the changes that may have an impact on why the experiment is not working as 
expected. The other code changes from UPISAS were already commited to the repository before the 
assignment was given.