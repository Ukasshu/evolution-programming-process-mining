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
import functools


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
        
        incl = self.all_tasks_number_ok(tokens)
        if incl < 0:
            return incl
        corr = self.are_gotos_correct(tokens, compiler)
        if corr != 0:
            return corr
        comp = self.compiles(compiler, phenotype)
        if comp == 0:
            return -1

        simple_graph = compiler.simplify_graph()
        max_trace = [(0.0, [], [])] * len(self.reader.simple_traces)
        markings = set()

        fitn = self.fitness(simple_graph, compiler, max_trace, markings)
        simp = self.simplicity(simple_graph, compiler)
        prec = self.precision(markings, max_trace, simple_graph)

        return fitn * 0.7 + simp * 0.1  + prec * 0.2

    def all_tasks_number_ok(self, tokens):
        task_tokens = list(filter(lambda tk: tk.startswith("task("), tokens))

        task_numbers_ok = list(map(lambda tk: int(re.search(r"task\(([0-9]+)\)", tk).group(1)) < self.reader.number_of_tasks,
                              task_tokens))

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
            return 0

    def fitness(self, simple_graph, compiler, max_trace, markings):
        """ FITNESS """
        traces = self.reader.simple_traces

        self.check_trace([("start", 0)], [], [], simple_graph, compiler, max_trace, markings, range(len(traces)))

        return sum(m[0] for m in max_trace) / len(traces) * 100

    def check_trace(self, curr, curr_trace, path, simple_graph, compiler, max_trace, markings, flwd_trcs):
        for nxt in bpmn_fitness.get_all_nexts(curr, simple_graph):
            self.make_a_step(curr, curr_trace, path, simple_graph, nxt, compiler, max_trace, markings, flwd_trcs)

    def make_a_step(self, curr, curr_trace, path, simple_graph, next_step, compiler, max_trace, markings, flwd_trcs):
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
                pass
            elif type_of_next == "task":
                task_num = simple_graph[next_step[0]]["num"]

                new_flwd_trcs = list(filter(lambda tr_num: self.check_task_in_traces(max_trace, curr_trace, path, task_num, tr_num), flwd_trcs))

                if len(new_flwd_trcs) > 0:
                    new_curr = copy.copy(curr)
                    new_curr.remove(next_step[1])
                    new_curr.append((next_step[0], 0))
                    new_path = copy.copy(path)
                    new_path.append(next_step)
                    new_curr_trace = copy.copy(curr_trace)
                    new_curr_trace.append(task_num)
                    self.check_trace(new_curr, new_curr_trace, new_path, simple_graph, compiler, max_trace, markings, new_flwd_trcs)
                else:
                    new_curr_trace = copy.copy(curr_trace)
                    new_curr_trace.append(task_num)
                    markings.add(tuple(new_curr_trace))
                    pass
                
            elif type_of_next == "par":
                new_curr = copy.copy(curr)
                new_curr.remove(next_step[1])
                new_curr.extend([(next_step[0], nmb) for nmb in range(1, len(simple_graph[next_step[0]]["next"]) + 1)])
                new_path = copy.copy(path)
                new_path.append(next_step)
                self.check_trace(new_curr, curr_trace, new_path, simple_graph, compiler, max_trace, markings, flwd_trcs)
            elif type_of_next == "epar":
                have_it_next = [cr for cr in curr if bpmn_fitness.has_next(cr, next_step[0], simple_graph)]
                if simple_graph[next_step[0]]["req_conn"] == len(have_it_next):
                    new_curr = [cr for cr in curr if cr not in have_it_next]
                    new_curr.append((next_step[0], 0))
                    new_path = copy.copy(path)
                    new_path.extend(list(map(lambda h: (next_step[0], h), have_it_next)))
                    self.check_trace(new_curr, curr_trace, new_path, simple_graph, compiler, max_trace, markings, flwd_trcs)
            elif type_of_next == "end":
                markings.add(tuple(curr_trace))
                self.count_max_traces_for_path_end(max_trace, curr_trace, path, flwd_trcs)
                pass
            
        except:
            traceback.print_exc()
            pprint.pprint(simple_graph)
            pprint.pprint(compiler.graph, width=1)


    def check_task_in_traces(self, max_trace, curr_trace, path, task_num, tr_num):
        try:
            res = self.reader.simple_traces[tr_num][len(curr_trace)] == task_num
        except IndexError:
            res = False
        if not res:
            new_curr_trace = copy.copy(curr_trace)
            new_curr_trace.append(task_num)
            fit_par = len(curr_trace) / max(len(new_curr_trace), len(self.reader.simple_traces[tr_num])) * 0.5
            max_trace[tr_num] = max(max_trace[tr_num], (fit_par, new_curr_trace, path), key=lambda el: (el[0], -len(el[1]), -len(el[2])))
        return res

    def count_max_traces_for_path_end(self, max_trace, curr_trace, path, flwd_trcs):
        for idx in flwd_trcs:
            tr = self.reader.simple_traces[idx]
            max_idx = min(len(tr), len(curr_trace))
            i = 0
            while i < max_idx and tr[i] == curr_trace[i]:
                i+= 1
            else:
                res = i / max(len(tr), len(curr_trace))
                max_trace[idx] = max(max_trace[idx], (res, curr_trace, path), key=lambda el: (el[0], -len(el[1]), -len(el[2])))

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
        task_nums = [simple_graph[nd]["num"] for nd in simple_graph if simple_graph[nd]["type"] == "task"]
        duplicates_number = len(task_nums) - len(set(task_nums))

        number_of_included_tasks = sum(
            ["task" + str(i) in compiler.simple_graph for i in range(self.reader.number_of_tasks)])
        missing_tasks = compiler.xes_reader.number_of_tasks - number_of_included_tasks

        loop_tasks = list(set(compiler.loop_tasks))
        loop_tasks.sort()

        is_really_loop_task = [self.reader.max_occurences[simple_graph[t]["num"]] > 1 for t in loop_tasks]

        return (1 - ((len(is_really_loop_task) - sum(is_really_loop_task)) / len(task_nums))) * (1 - (missing_tasks + duplicates_number) / (self.reader.number_of_tasks + len(task_nums))) * 100

    def precision(self, markings, max_traces, simple_graph):
        """PRECISION"""
        sum_of_logs_behaviors = 0

        trcs = list(map(lambda mt: mt[1], max_traces))
        used_traces = list(map(lambda trc: trcs.count(trc), trcs))
        for i in range(len(max_traces)):
            if tuple(max_traces[i][1]) in markings:
                sum_of_logs_behaviors += max_traces[i][0] / used_traces[i]


        paths = list(map(lambda mt: mt[2], max_traces))
        visited_nodes = functools.reduce(lambda a,b: a+b, paths)
        unique_visited_nodes_names = set(list(map(lambda nd: nd[0], visited_nodes)))

        res = len(unique_visited_nodes_names) / (len(simple_graph) - 2) * (sum_of_logs_behaviors / len(markings))

        return res * 100

    def generalization(self, precision):
        """GENERALIZATION"""
        return 100


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
