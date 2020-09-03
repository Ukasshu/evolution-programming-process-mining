package pl.edu.agh.kis;

import org.camunda.bpm.model.bpmn.Bpmn;
import org.camunda.bpm.model.bpmn.BpmnModelInstance;
import org.camunda.bpm.model.bpmn.instance.Process;
import org.camunda.bpm.model.bpmn.instance.*;

import java.io.File;
import java.io.IOException;

public class BPMNModel {

    public static BpmnModelInstance modelInstance = Bpmn.createEmptyModel();

    public static void main(String[] args) throws IOException {
        createModel();
    }


    public static void createModel() throws IOException {

        // validate and write model to file
        try {
            modelInstance = getInstance();
            Bpmn.validateModel(modelInstance);
            File file = new File("diagram.xml");
            Bpmn.writeModelToFile(file, modelInstance);
            System.out.println("OK");
            System.exit(0);
        }
        catch(Exception e) {
            System.out.println("FAIL");
            System.exit(1);
        }
    }

    public static BpmnModelInstance getInstance() {
        // here will be added code
        return Bpmn.createProcess().startEvent("start").userTask("task0").name("register request").parallelGateway("gat0").userTask("task1").name("decide").parallelGateway("egat0").moveToNode("gat0").userTask("task2").name("check ticket").connectTo("egat0").moveToNode("gat0").userTask("task3").name("examine thoroughly").connectTo("egat0").moveToNode("egat0").userTask("task4").name("reject request").endEvent("end").done();}}