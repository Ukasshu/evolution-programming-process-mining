BpmnModelInstance modelInstance = Bpmn.createEmptyModel();

Definitions definitions = modelInstance.newInstance(Definitions.class);
definitions.setTargetNameSpace("http://camunda.org/examples");
modelInstance.setDefinitions(definitions);

Process process = modelInstance.newInstance(Process.class);
process.setId("process");
definitions.addChildElement(process);