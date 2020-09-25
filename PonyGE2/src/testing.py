from fitness.bpmn_fitness_2 import bpmn_fitness_2
from fitness.bpmn.compiler import Compiler
from fitness.bpmn.xes_reader import XESReader

reader = XESReader("repair-example.xes")
reader.read_xes()

# str_to_cmp = "start task(4) task(1) task(0) exsplit exsplit par ex task(10) next back task(3) next ex task(6) task(5) task(11) next back back ex task(10) next back exsplit end next end next end back next task(8) exsplit end next exsplit exsplit end next task(10) exsplit end next end next end back next task(3) end next task(7) loop loop task(11) back back exsplit ex task(10) next back end next end back back next end back back next task(9) exsplit end next end back next end back next end back"
str_to_cmp = "start par task(4) task(0) next task(1) back exsplit loop loop ex task(6) next task(3) next task(5) back back back loop loop ex loop loop ex task(8) next task(3) back back back next task(11) next task(10) back back back exsplit exsplit loop loop ex task(6) next task(3) back back back exsplit task(7) loop loop ex task(6) next task(3) back back back end next task(8) end next end back next task(2) end next task(8) end back next task(8) end next task(8) end back next end back"

compiler = Compiler(" ", reader)
compiler.compile(str_to_cmp)
compiler.simplify_graph()

# compiler.simple_graph["task3"]["next"].append("end")
# compiler.simple_graph["task6"]["next"].append("end")
# compiler.simple_graph["task7"]["next"].append("end")
# compiler.simple_graph["task9"]["next"].append("end")

fit = bpmn_fitness_2()

fit.reader = reader

class Obj:
    pass


a = Obj()
a.phenotype = str_to_cmp


max_trace = [(0, [], [])] * len(reader.simple_traces)
markings = set()


fitn = fit.fitness(compiler.simple_graph, compiler, max_trace, markings)
simp = fit.simplicity(compiler.simple_graph, compiler)
prec = fit.precision(markings, max_trace, compiler.simple_graph)
over = 0.7 * fitn + 0.1 * simp + 0.2 * prec

print("Overall   : " + str(over))
print("Fitness   : " + str(fitn))
print("Simplicity: " + str(simp))
print("Precision : " + str(prec))

