import glob
import os
import subprocess

from fitness.bpmn.xes_reader import XESReader
from fitness.bpmn.compiler import Compiler
from algorithm.parameters import params

list_of_files = glob.glob('..\\results\\*') # * means all if need specific format then *.csv
latest_dir = max(list_of_files, key=os.path.getctime)

filename = latest_dir + "\\best.txt"

with open(filename, 'r') as file:
    data = file.readlines()

reader = XESReader(params["TRACES_XES_FILE"])
reader.read_xes()

compiler = Compiler(" ", reader)

program = "".join(compiler.compile(data[4].rstrip()))

template = open("../../bpmn-model/src/main/java/pl/edu/agh/kis/BPMNModel_template").read()

f = open("../../bpmn-model/src/main/java/pl/edu/agh/kis/BPMNModel.java", "w")
f.write(template + program)
f.close()

status = subprocess.call('java -cp src/main/resources/* src/main/java/pl/edu/agh/kis/BPMNModel.java', cwd='../../bpmn-model', shell=False)
if status != 0:
    raise Exception("Validation failed")