from fitness.bpmn_fitness_2 import bpmn_fitness_2
from fitness.bpmn.compiler import Compiler
from fitness.bpmn.xes_reader import XESReader

reader = XESReader("repair-example.xes")
reader.read_xes()

str_to_cmp = "start par task(3) task(0) next task(0) loop task(5) back back loop task(4) back loop task(7) back exsplit par loop do task(4) repeat_after back task(7) back task(7) next task(2) back task(1) end next end next task(2) end back" 

compiler = Compiler(" ", reader)
compiler.compile(str_to_cmp)
compiler.simplify_graph()

fit = bpmn_fitness_2()

class Obj:
    pass


a = Obj()
a.phenotype = str_to_cmp


max_trace = [(0, [], [])] * len(reader.simple_traces)
markings = set()

over = fit.evaluate(a)
fitn = fit.fitness(compiler.simple_graph, compiler, max_trace, markings)
simp = fit.simplicity(compiler.simple_graph, compiler)
prec = fit.precision(markings, max_trace, compiler.simple_graph)


print("Overall   : " + str(over))
print("Fitness   : " + str(fitn))
print("Simplicity: " + str(simp))
print("Precision : " + str(prec))

