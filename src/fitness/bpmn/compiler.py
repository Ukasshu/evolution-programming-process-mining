import re
import copy
import json
import traceback

class Compiler:
    def __init__(self, delimiter, xes_reader):
        self.delimiter = delimiter
        self.par_tasks = set()
        self.loop_tasks = set()
        self.program = []
        self.graph = {}
        self.xes_reader = xes_reader
        self.simple_graph = {}

    def compile(self, string_to_compile):
        self.par_tasks = set()
        self.loop_tasks = set()
        self.program = [] 
                
        tokens = string_to_compile.split(self.delimiter)

        gateway_count = 0  # OK
        gateway_stack = []  # OK

        task_count = 0

        last_element = None  # OK

        additional_connections = []  # OK

        started = False  # OK
        ended = False  # OK

        for token in tokens:
            if token == "start" and not started:
                #start
                started = True
                self.program.append(".startEvent(\"start\")")
                self.graph["start"] = {
                    "next": [],
                    "type": "start",
                    "name": "start"
                }
                last_element = "start"
                ###
            elif token.startswith("task("):
                #task
                match = re.search(r"\(([0-9]+)\)", token)
                task_num = match.group(1)
                task_id = "task" + task_count
                task_count += 1
                self.program.append(".userTask(\"" + task_id + "\").name(\"" + self.xes_reader.tasks[int(task_num)] + "\")")
                self.graph[last_element]["next"].append(task_id)
                self.graph[task_id] = {
                    "next": [],
                    "type": "task",
                    "name": task_id,
                    "num" : task_num
                }

                last_element = task_id

                if any([gat["type"] == "par" for gat in gateway_stack]):
                    # if any(list(map(lambda gat: gat["type"].startswith("par"), gateway_stack))):
                    self.par_tasks.add(task_id)
                if any([gat["type"] in ["loop", "do_repeat"] for gat in gateway_stack]):
                    self.loop_tasks.add(task_id)
                ###
            elif token == "loop":
                #loop
                curr_gat = {
                    "next": [],
                    "name": "gat" + str(gateway_count),
                    "type": "loop"
                }
                gateway_stack.append(curr_gat)
                self.program.append(".exclusiveGateway(\"" + curr_gat["name"] + "\")")
                self.graph[last_element]["next"].append(curr_gat["name"])
                self.graph[curr_gat["name"]] = curr_gat
                last_element = curr_gat["name"]
                gateway_count += 1
                ###
            elif token == "par":
                #par
                curr_gat = {
                    "next": [],
                    "name": "gat" + str(gateway_count),
                    "type": "par",
                    "end": False
                }
                gateway_stack.append(curr_gat)
                self.program.append(".parallelGateway(\"" + curr_gat["name"] + "\")")
                self.graph[last_element]["next"].append(curr_gat["name"])
                self.graph[curr_gat["name"]] = curr_gat
                last_element = curr_gat["name"]
                gateway_count += 1
                ###
            elif token == "ex":
                #ex
                curr_gat = {
                    "next": [],
                    "name": "gat" + str(gateway_count),
                    "type": "ex",
                    "end": False
                }
                gateway_stack.append(curr_gat)
                self.program.append(".exclusiveGateway(\"" + curr_gat["name"] + "\")")
                self.graph[last_element]["next"].append(curr_gat["name"])
                self.graph[curr_gat["name"]] = curr_gat
                last_element = curr_gat["name"]
                gateway_count += 1
                ###
            elif token == "exsplit":
                #exsplit
                curr_gat = {
                    "next": [],
                    "name": "gat" + str(gateway_count),
                    "type": "split"
                }
                gateway_stack.append(curr_gat)
                self.program.append(".exclusiveGateway(\"" + curr_gat["name"] +"\")")
                self.graph[last_element]["next"].append(curr_gat["name"])
                self.graph[curr_gat["name"]] = curr_gat
                last_element = curr_gat["name"]
                gateway_count += 1
                ###
            elif token == "do":
                #do
                curr_gat = {
                    "next": [],
                    "name": "gat" + str(gateway_count),
                    "type": "do_repeat"
                }
                gateway_stack.append(curr_gat)
                self.program.append(".exclusiveGateway(\"" + curr_gat["name"] + "\")")
                self.graph[last_element]["next"].append(curr_gat["name"])
                self.graph[curr_gat["name"]] = curr_gat
                last_element = curr_gat["name"]
                gateway_count += 1
                ###
            elif token == "repeat_after":
                #repeat
                last_gateway = gateway_stack[-1]
                self.program.append(".exclusiveGateway(\"e" + last_gateway["name"] + "\")")
                self.graph[last_element]["next"].append("e" + last_gateway["name"])
                self.graph["e" + last_gateway["name"]] = {
                    "next": [],
                    "name": "e" + last_gateway["name"],
                    "type": "e" + last_gateway["type"]
                }
                last_element = "e" + last_gateway["name"]
                ###
            elif token == "next":
                #next
                last_gateway = gateway_stack[-1]
                if last_gateway["type"] == "split":
                    self.program.append(".moveToNode(\"" + last_gateway["name"] +"\")")
                elif last_gateway["type"] == "ex":
                    if not last_gateway["end"]:
                        self.program.append(".exclusiveGateway(\"e" + last_gateway["name"] + "\")")
                        self.graph["e" + last_gateway["name"]] = {
                            "next": [],
                            "name": "e" + last_gateway["name"],
                            "type": "e" + last_gateway["type"]
                        }
                        last_gateway["end"] = True
                    else:
                        self.program.append(".connectTo(\"e" + last_gateway["name"] + "\")")
                    self.graph[last_element]["next"].append("e" + last_gateway["name"])
                    self.program.append(".moveToNode(\"" + last_gateway["name"] +"\")")
                elif last_gateway["type"] == "par":
                    if not last_gateway["end"]:
                        self.program.append(".parallelGateway(\"e" + last_gateway["name"] + "\")")
                        self.graph["e" + last_gateway["name"]] = {
                            "next": [],
                            "name": "e" + last_gateway["name"],
                            "type": "e" + last_gateway["type"]
                        }
                        last_gateway["end"] = True
                    else:
                        self.program.append(".connectTo(\"e" + last_gateway["name"] + "\")")
                    self.graph[last_element]["next"].append("e" + last_gateway["name"])
                    self.program.append(".moveToNode(\"" + last_gateway["name"] +"\")")
                else:
                    raise Exception("Wrong token found")
                last_element = last_gateway["name"]
                ###
            elif token == "back":
                #back
                last_gateway = gateway_stack[-1]
                if last_gateway["type"] == "loop":
                    self.program.append(".connectTo(\"" + last_gateway["name"] +"\")")
                    self.program.append(".moveToNode(\"" + last_gateway["name"] + "\")")
                    self.graph[last_element]["next"].append(last_gateway["name"])
                    gateway_stack.pop()
                    last_element = last_gateway["name"]
                elif last_gateway["type"] == "split":
                    gateway_stack.pop()
                    if len(gateway_stack) > 0:
                        last_element = gateway_stack[-1]["name"]
                    else:
                        last_element = None
                elif last_gateway["type"] in ["ex", "par"]:
                    self.program.append(".connectTo(\"e" + last_gateway["name"] +"\")")
                    self.program.append(".moveToNode(\"e" + last_gateway["name"] + "\")")
                    self.graph[last_element]["next"].append("e" + last_gateway["name"])
                    gateway_stack.pop()
                    last_element = "e" + last_gateway["name"]
                elif last_gateway["type"] == "do_repeat":
                    self.program.append(".connectTo(\"" + last_gateway["name"] + "\")")
                    self.program.append(".moveToNode(\"e" + last_gateway["name"] + "\")")
                    self.graph[last_element]["next"].append(last_gateway["name"])
                    gateway_stack.pop()
                    last_element = "e" + last_gateway["name"]
                ###
            elif token.startswith("goto("):
                #goto
                match = re.search(r"\(([a-z0-9]+)\)", token)
                node_name = match.group(1)
                additional_connections.append({
                    "from": last_element,
                    "to": node_name
                })
                self.graph[last_element]["next"].append(node_name)
                ###
            elif token == "end":
                if not ended:
                    self.program.append(".endEvent(\"end\")")
                    ended = True
                    self.graph["end"] = {
                        "next": [],
                        "name": "end",
                        "type": "end"
                    }
                else:
                    additional_connections.append({
                        "from": last_element,
                        "to": "end"
                    })
                self.graph[last_element]["next"].append("end")
            else:
                raise Exception("Unknown token")

        for conn in additional_connections:
            self.program.append(".moveToNode(\"" + conn["from"] + "\")")
            self.program.append(".connectTo(\"" + conn["to"] + "\")")

        self.program.append(".done();}}")

        return self.program

    def simplify_graph(self):
        try:
            simple_graph = copy.deepcopy(self.graph)

            # epars - count req_conn ###
            epar_gat_ids = list(filter(lambda key: simple_graph[key]["type"] == "epar", simple_graph.keys()))
            for epar_id in epar_gat_ids:
                simple_graph[epar_id]["req_conn"] = len([id for id in list(simple_graph.keys()) if epar_id in simple_graph[id]['next']])

            # pars - ###
            par_gat_ids = list(filter(lambda key: simple_graph[key]["type"] == "par", simple_graph.keys()))
            for par_id in par_gat_ids:
                simple_graph[par_id]["next"] = list(map(lambda el: [el], simple_graph[par_id]["next"]))

            # exclusive gateways to multiple connections ###
            ex_gat_ids = list(filter(lambda key: simple_graph[key]["type"] in ["ex", "eex", "loop", "do_repeat", "edo_repeat", "split"], simple_graph.keys()))

            for ex_id in ex_gat_ids:
                if ex_id in simple_graph[ex_id]["next"]:
                    simple_graph[ex_id]["next"] = list(filter(ex_id.__ne__, simple_graph[ex_id]["next"]))
            
                for el in list(simple_graph.keys()):
                    if simple_graph[el]["type"] != "par" and ex_id in simple_graph[el]["next"]:
                        simple_graph[el]["next"] = list(filter(ex_id.__ne__, simple_graph[el]["next"]))
                        simple_graph[el]["next"].extend(simple_graph[ex_id]["next"])
                    elif simple_graph[el]["type"] == "par":
                        for idx in range(len(simple_graph[el]["next"])):
                            if ex_id in simple_graph[el]["next"][idx]:
                                simple_graph[el]["next"][idx] = list(filter(ex_id.__ne__, simple_graph[el]["next"][idx]))
                                simple_graph[el]["next"][idx].extend(simple_graph[ex_id]["next"])
                
                simple_graph.pop(ex_id)

            self.simple_graph = simple_graph

            return simple_graph
        except:
            traceback.print_exc()
            print(str(simple_graph))