from fitness.bpmn_fitness import bpmn_fitness
from fitness.bpmn.compiler import Compiler
from fitness.bpmn.xes_reader import XESReader

reader = XESReader("repair-example.xes")
reader.read_xes()

str_to_cmp = "start task(4) task(1) task(0) par task(3) next do ex task(8) task(7) next task(6) task(5) back task(11) task(10) repeat_after task(9) back back task(2) end"

compiler = Compiler(" ", reader)
compiler.compile(str_to_cmp)
compiler.simplify_graph()


fit = bpmn_fitness()

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

