from algorithm.parameters import params
from fitness.base_ff_classes.base_ff import base_ff
from fitness.bpmn.compiler import Compiler
from fitness.bpmn.xes_reader import XESReader
import re
import subprocess

class bpmn_fitness(base_ff):
    """Fitness function for matching a string. Takes a string and returns
    fitness. Penalises output that is not the same length as the target.
    Penalty given to individual string components which do not match ASCII
    value of target."""

    maximise = True

    tasks_number = 5
     

    def __init__(self):
        # Initialise base fitness function class.
        super().__init__()
        
        # Set target string.
        self.target = params['TARGET']
        self.compiler = Compiler("{::}")
        self.reader = XESReader(params['TRACES_XES_FILE'])
        self.reader.read_xes()

    def evaluate(self, ind, **kwargs):
        phenotype = ind.phenotype

        tokens = phenotype.split("{::}")

        return self.compiles(phenotype) * self.all_tasks_included(tokens) * self.are_gotos_correct(tokens)


    def all_tasks_included(self, tokens):
        task_tokens = list(filter(lambda tk: tk.startswith("task("), tokens))
        unique_task_tokens = list(set(task_tokens))
        return len(unique_task_tokens) * int(len(task_tokens) == len(unique_task_tokens))  * int(len(unique_task_tokens) <= self.tasks_number)

    def are_gotos_correct(self, tokens):
        task_gotos = list(filter(lambda tk: tk.startswith("goto(task"), tokens))
        gat_gotos = list(filter(lambda tk: tk.startswith("goto(gat"), tokens))
        gat_tokens = list(filter(lambda tk: tk in ["par", "ex", "exsplit", "loop"], tokens))

        task_gotos_correctness = list(map(lambda tk: int(re.search(r"\(task([0-9]+)\)", tk).group(1)) < self.tasks_number and tk not in self.compiler.par_tasks, task_gotos))
        gat_gotos_correctness = list(map(lambda tk: int(re.search(r"\(gat([0-9]+)\)", tk).group(1)) < len(gat_tokens), gat_gotos))

        wrong_gotos = len(task_gotos_correctness) - sum(task_gotos_correctness) + len(gat_gotos_correctness) - sum(gat_gotos_correctness)

        if (wrong_gotos > 0):
            return -wrong_gotos
        else:
            return 1



    def compiles(self, phenotype):
        # status = 0
        try:
            program = "".join(self.compiler.compile(phenotype))

            template = open("../../bpmn-model/src/main/java/pl/edu/agh/kis/BPMNModel_template").read()

            f = open("../../bpmn-model/src/main/java/pl/edu/agh/kis/BPMNModel.java", "w")
            f.write(template + program)
            f.close()

            # status = subprocess.call('java -cp src/main/resources/* src/main/java/pl/edu/agh/kis/BPMNModel.java', cwd='../../bpmn-model', shell=False)
            # if status != 0:
            #     raise Exception("Validation failed")
        except:
            # print(e)
            return 0

        return 1

    # def 

        
