from algorithm.parameters import params
from fitness.base_ff_classes.base_ff import base_ff
from fitness.bpmn.compiler import Compiler
from fitness.bpmn.xes_reader import XESReader
from unittest.mock import ANY
import re
import subprocess

class bpmn_fitness(base_ff):
    """Fitness function for matching a string. Takes a string and returns
    fitness. Penalises output that is not the same length as the target.
    Penalty given to individual string components which do not match ASCII
    value of target."""

    maximise = True     

    def __init__(self):
        # Initialise base fitness function class.
        super().__init__()
        
        self.target = params['TARGET']
        self.reader = XESReader(params['TRACES_XES_FILE'])
        self.reader.read_xes()
        self.compiler = Compiler(" ", self.reader)
        

    def evaluate(self, ind, **kwargs):
        self.visited_edges = []
        
        phenotype = ind.phenotype

        tokens = phenotype.split(" ")

        return self.compiles(phenotype) * self.all_tasks_included(tokens) * self.are_gotos_correct(tokens)


    def all_tasks_included(self, tokens):
        task_tokens = list(filter(lambda tk: tk.startswith("task("), tokens))
        unique_task_tokens = list(set(task_tokens))

        task_numbers_ok = all(map(lambda tk: int(re.search(r"task\(([0-9]+)\)", tk).group(1)) < self.reader.number_of_tasks, unique_task_tokens))

        return len(unique_task_tokens) * int(len(task_tokens) == len(unique_task_tokens))  * int(len(unique_task_tokens) <= self.reader.number_of_tasks) * int(task_numbers_ok)

    def are_gotos_correct(self, tokens):
        task_gotos = list(filter(lambda tk: tk.startswith("goto(task"), tokens))
        gat_gotos = list(filter(lambda tk: tk.startswith("goto(gat"), tokens))
        gat_tokens = list(filter(lambda tk: tk in ["par", "ex", "exsplit", "loop"], tokens))

        task_gotos_correctness = list(map(lambda tk: int(re.search(r"\(task([0-9]+)\)", tk).group(1)) < self.reader.number_of_tasks and tk not in self.compiler.par_tasks, task_gotos))
        gat_gotos_correctness = list(map(lambda tk: int(re.search(r"\(gat([0-9]+)\)", tk).group(1)) < len(gat_tokens), gat_gotos))

        wrong_gotos = len(task_gotos_correctness) - sum(task_gotos_correctness) + len(gat_gotos_correctness) - sum(gat_gotos_correctness)

        if (wrong_gotos > 0):
            return -wrong_gotos
        else:
            return 1

    """ FITNESS """
    def fitness(self):
        self.visited_edges = set()
        counter = 0

        graph = self.compiler.graph
        traces = self.reader.simple_traces
        
        for trace in traces:
            next_elements = [[("start", graph["start"]["next"])]]
            self.visited_edges
            fail = False
            i = 0

            task_to_reach = [trace[0]]
            task_searched = [False] * len(trace)

            while not fail and i < len(trace):
                

                if any((ANY, trace[i]) in element for element in next_elements):
                    next_elements = [element for i in range(2)]
                    next_elements = next_elements + list(map(lambda tk: (trace[i], tk) ,graph[trace[i]]["next"]))
                    self.visited_edges.add(map(lambda n: (), graph[trace[i]]["next"]))
                    i += 1
                    task_to_reach = [trace[i]]
                    noop = False
                    # continue
                # if gats:

                # if noop:
                    
    def find_way_to_task(self, start_points, next_task):
        paths = start_points
        graph = self.compiler.graph
        while not paths:
            next_paths = list(map(lambda path: list(map(lambda n: path + (n,), graph[path[-1]]["next"])) , [p for p in paths if p[-1] != next_task]))
            next_paths = [branch for path in next_paths for branch in path] + [p for p in paths if p[-1] == next_task]
            if all([path[-1] == next_task for path in next_paths]):
                return next_paths
            paths = [path for path in next_paths if bpmn_fitness.path_valid(path, next_task)]
        return []

    @staticmethod
    def path_valid(path, task):
        return len(set(path)) == len(path) and not (path[-1].startswith("task") and path[-1] != task)
            










    def compiles(self, phenotype):
        # status = 0
        try:
            self.compiler.compile(phenotype)

            """ TO GDZIEŚ KIEDYŚ NA KOŃCU """
            # program = "".join(self.compiler.compile(phenotype))

            # template = open("../../bpmn-model/src/main/java/pl/edu/agh/kis/BPMNModel_template").read()

            # f = open("../../bpmn-model/src/main/java/pl/edu/agh/kis/BPMNModel.java", "w")
            # f.write(template + program)
            # f.close()

            # status = subprocess.call('java -cp src/main/resources/* src/main/java/pl/edu/agh/kis/BPMNModel.java', cwd='../../bpmn-model', shell=False)
            # if status != 0:
            #     raise Exception("Validation failed")
        except:
            # print(e)
            return 0

        return 1

    # def 

        
