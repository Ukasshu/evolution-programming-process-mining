import glob
import os
import subprocess
import sys

from fitness.bpmn.xes_reader import XESReader
from fitness.bpmn.compiler import Compiler
from algorithm.parameters import params

print("Wprowadź rozwiązanie do wygenerowania: ")

input = sys.stdin.readline().rstrip()

reader = XESReader(params["TRACES_XES_FILE"])
reader.read_xes()

compiler = Compiler(" ", reader)

program = "".join(compiler.compile(input))

template = open("../../bpmn-model/src/main/java/pl/edu/agh/kis/BPMNModel_template").read()

f = open("../../bpmn-model/src/main/java/pl/edu/agh/kis/BPMNModel.java", "w")
f.write(template + program)
f.close()

status = subprocess.call('java -cp src/main/resources/* src/main/java/pl/edu/agh/kis/BPMNModel.java', cwd='../../bpmn-model', shell=False)
if status != 0:
    raise Exception("Validation failed")