from fitness.bpmn.xes_reader import XESReader
from algorithm.parameters import params

with open("../grammars/bpmn-lang-template", 'r') as file:
    data = file.readlines()

reader = XESReader(params["TRACES_XES_FILE"])
reader.read_xes()

data[2] = "<numOfTasks> ::= GE_RANGE:" + str(reader.number_of_tasks) + "\n"

with open("../grammars/bpmn-lang.bnf", 'w') as file:
    file.writelines(data)
