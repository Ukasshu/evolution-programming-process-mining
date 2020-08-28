from algorithm.parameters import params
from fitness.base_ff_classes.base_ff import base_ff
from fitness.bpmn.compiler import Compiler
from fitness.bpmn.xes_reader import XESReader
from unittest.mock import ANY
import re
# import subprocess
import copy
import traceback
import pprint


class bpmn_fitness(base_ff):
    """Fitness BPMN"""

    maximise = True

    def __init__(self):
        # Initialise base fitness function class.
        super().__init__()

        self.target = params['TARGET']
        self.reader = XESReader(params['TRACES_XES_FILE'])
        self.reader.read_xes()

    def evaluate(self, ind, **kwargs):
        self.visited_edges = []

        phenotype = ind.phenotype

        compiler = Compiler(" ", self.reader)

        tokens = phenotype.split(" ")
        corr = self.are_gotos_correct(tokens, compiler)
        comp = self.compiles(compiler, phenotype)
        incl = self.all_tasks_included(tokens)
        if incl < 0:
            return incl
        elif corr != 1:
            return corr
        elif comp == 0:
            return incl

        simple_graph = compiler.simplify_graph()
        max_trace = [(0.0, [])] * len(self.reader.simple_traces)

        fitn = self.fitness(simple_graph, compiler, max_trace)
        simp = self.simplicity(simple_graph, compiler)
        prec = self.precision(simple_graph, max_trace)
        gene = 100 #self.generalization(max_trace, simple_graph)

        # return (fitn * simp * prec * gene) ** (0.25)
        return fitn  * 0.55 + simp * 0.35  + prec * 0.1 #+ gene * 0.1

    def all_tasks_included(self, tokens):
        task_tokens = list(filter(lambda tk: tk.startswith("task("), tokens))

        task_numbers_ok = map(lambda tk: int(re.search(r"task\(([0-9]+)\)", tk).group(1)) < self.reader.number_of_tasks,
                              set(task_tokens))

        if all(task_numbers_ok):
            return 0
        else:
            return -sum(list(map(lambda o: not o, task_numbers_ok)))

    def are_gotos_correct(self, tokens, compiler):
        task_gotos = list(filter(lambda tk: tk.startswith("goto(task"), tokens))
        gat_gotos = list(filter(lambda tk: tk.startswith("goto(gat"), tokens))
        gat_tokens = list(filter(lambda tk: tk in ["par", "ex", "exsplit", "loop"], tokens))

        task_gotos_correctness = list(map(lambda tk: tk not in compiler.par_tasks and tk in compiler.graph, task_gotos))
        gat_gotos_correctness = list(
            map(lambda tk: int(re.search(r"\(gat([0-9]+)\)", tk).group(1)) < len(gat_tokens) and tk in compiler.graph,
                gat_gotos))

        wrong_gotos = len(task_gotos_correctness) - sum(task_gotos_correctness) + len(gat_gotos_correctness) - sum(
            gat_gotos_correctness)

        if wrong_gotos > 0:
            return -wrong_gotos
        else:
            return 1

    def fitness(self, simple_graph, compiler, max_trace):
        """ FITNESS """
        traces = self.reader.simple_traces

        for i, trace in enumerate(traces):
            self.check_trace([("start", 0)], 0, [], (trace, i), simple_graph, compiler, max_trace)

        if all([m[0] >= 0.6 for m in max_trace]):
            print(simple_graph)

        return sum(m[0] for m in max_trace) / len(traces) * 100

    def check_trace(self, curr, index, path, trace, simple_graph, compiler, max_trace):
        for nxt in bpmn_fitness.get_all_nexts(curr, simple_graph):
            self.make_a_step(curr, index, path, trace, simple_graph, nxt, compiler, max_trace)

    def make_a_step(self, curr, index, path, trace, simple_graph, next_step, compiler, max_trace):
        try:
            # wrong_way = False
            is_task = [el[0].startswith("task") for el in path[::-1]]
            if any(is_task):
                tsk_pos = is_task.index(True)
                sublist = path[::-1][0:tsk_pos]
                wrong_way = len(set(sublist)) != len(sublist)
            else:
                wrong_way = len(set(path)) != len(path)
            type_of_next = simple_graph[next_step[0]]["type"]
            if wrong_way:
                res = index / len(trace[0])
                max_trace[trace[1]] = max(max_trace[trace[1]], (res, path), key=lambda el: (el[0], -len(el[1])))
                # pass
            elif type_of_next == "task":
                if index < len(trace[0]) and next_step[0] == trace[0][index]:
                    new_curr = copy.deepcopy(curr)
                    new_curr.remove(next_step[1])
                    new_curr.append((next_step[0], 0))
                    new_path = copy.deepcopy(path)
                    new_path.append(next_step)
                    self.check_trace(new_curr, index + 1, new_path, trace, simple_graph, compiler, max_trace)
                else:  # include it? #nah
                    res = index / len(trace[0])
                    max_trace[trace[1]] = max((res, path), max_trace[trace[1]], key=lambda el: (el[0], -len(el[1])))
            elif type_of_next == "par":
                new_curr = copy.deepcopy(curr)
                new_curr.remove(next_step[1])
                new_curr.extend([(next_step[0], nmb) for nmb in range(1, len(simple_graph[next_step[0]]["next"]) + 1)])
                new_path = copy.deepcopy(path)
                new_path.append(next_step)
                self.check_trace(new_curr, index, new_path, trace, simple_graph, compiler, max_trace)
            elif type_of_next == "epar":
                have_it_next = [cr for cr in curr if bpmn_fitness.has_next(cr, next_step[0], simple_graph)]
                if simple_graph[next_step[0]]["req_conn"] == len(have_it_next):
                    new_curr = [cr for cr in curr if cr not in have_it_next]
                    new_curr.append((next_step[0], 0))
                    new_path = copy.deepcopy(path)
                    new_path.extend(list(map(lambda h: (next_step[0], h), have_it_next)))
                    self.check_trace(new_curr, index, new_path, trace, simple_graph, compiler, max_trace)
                elif type_of_next == "end":
                    # new_curr = copy.deepcopy(path) ???
                    # new_curr.append("end") ????
                    if index == len(trace[0]):
                        res = index / len(trace[0])
                        max_trace[trace[1]] = max(max_trace[trace[1]], (res, path), key=lambda el: (el[0], -len(el[1])))
        except:
            traceback.print_exc()
            pprint.pprint(simple_graph)
            pprint.pprint(compiler.graph, width=1)

    @staticmethod
    def get_all_nexts(curr, simple_graph):
        nexts = []
        try:
            for node, nmb in curr:
                if simple_graph[node]["type"] == "par":
                    nexts.extend(list(map(lambda n: (n, (node, nmb)), simple_graph[node]["next"][nmb - 1])))
                else:
                    nexts.extend(list(map(lambda n: (n, (node, nmb)), simple_graph[node]["next"])))
        except:
            traceback.print_exc()
            print(simple_graph)
        return nexts

    @staticmethod
    def has_next(node, nxt, simple_graph):
        if simple_graph[node[0]]["type"] == "par":
            return nxt in simple_graph[node[0]]["next"][node[1] - 1]
        else:
            return nxt in simple_graph[node[0]]["next"]

    def simplicity(self, simple_graph, compiler):
        """SIMPLICITY"""
        non_par_edges = sum(
            [len(simple_graph[nd]["next"]) for nd in simple_graph.keys() if simple_graph[nd]["type"] != "par"])
        unique_non_par_edges = sum(
            [len(set(simple_graph[nd]["next"])) for nd in simple_graph.keys() if simple_graph[nd]["type"] != "par"])
        par_edges = sum([len(br) for nd in simple_graph.keys() if simple_graph[nd]["type"] == "par" for br in
                         simple_graph[nd]["next"]])
        unique_par_edges = sum(
            [len(set(br)) for nd in simple_graph.keys() if simple_graph[nd]["type"] == "par" for br in
             simple_graph[nd]["next"]])

        duplicate_edges = non_par_edges + par_edges - (unique_non_par_edges + unique_par_edges)

        number_of_included_tasks = sum(
            ["task" + str(i) in compiler.simple_graph for i in range(self.reader.number_of_tasks)])
        missing_tasks = compiler.xes_reader.number_of_tasks - number_of_included_tasks

        loop_tasks = list(set(compiler.loop_tasks))
        loop_tasks.sort()

        is_really_loop_task = [any([tr.count(t) > 1 for tr in self.reader.simple_traces]) for t in loop_tasks]

        nodes_number = len(simple_graph)
        tasks_number = len([el for el in simple_graph if simple_graph[el]["type"] in ["task", "start", "end"]])

        return (1 - ((len(is_really_loop_task) - sum(is_really_loop_task)) / self.reader.number_of_tasks)) *(1 - missing_tasks / self.reader.number_of_tasks) * 100

    def precision(self, simple_graph, max_traces):
        """PRECISION"""
        non_par_edges = sum(
            [len(simple_graph[nd]["next"]) for nd in simple_graph.keys() if simple_graph[nd]["type"] != "par"])
        par_edges = sum([len(br) for nd in simple_graph.keys() if simple_graph[nd]["type"] == "par" for br in
                         simple_graph[nd]["next"]])

        all_edges = non_par_edges + par_edges

        used_edges = len(set([el for max_t in max_traces for el in max_t[1]]))

        return (1 - (all_edges - used_edges)/all_edges) * 100

    def generalization(self, max_traces, simple_graph):
        """GENERALIZATION"""

        nodes_occurences = [el for max_t in max_traces for el in max_t[1]]

        sum_of_occurences = 0
        for nd in simple_graph:
            node_occurences = nodes_occurences.count((nd, ANY))
            if node_occurences == 0:
                node_occurences = 1
            if simple_graph[nd]["type"] == "epar":
                sum_of_occurences += (node_occurences / simple_graph[nd]["req_conn"]) ** (-0.5)
            elif nd not in ["start", "end"]:
                sum_of_occurences += (node_occurences ** (-0.5))

        num_of_nodes = len(simple_graph) - 2

        return (1 - sum_of_occurences/num_of_nodes) * 100


    @staticmethod
    def compiles(compiler, phenotype):
        # status = 0
        try:
            compiler.compile(phenotype)

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
