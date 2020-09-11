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
        return Bpmn.createProcess().startEvent("start").userTask("task0").name("Register+complete").userTask("task1").name("Analyze Defect+start").userTask("task2").name("Analyze Defect+complete").parallelGateway("gat0").userTask("task3").name("Inform User+complete").parallelGateway("egat0").moveToNode("gat0").exclusiveGateway("gat1").exclusiveGateway("gat2").userTask("task4").name("Repair (Simple)+start").userTask("task5").name("Repair (Simple)+complete").exclusiveGateway("egat2").moveToNode("gat2").userTask("task6").name("Repair (Complex)+start").userTask("task7").name("Repair (Complex)+complete").connectTo("egat2").moveToNode("egat2").userTask("task8").name("Test Repair+complete").userTask("task9").name("Test Repair+start").exclusiveGateway("egat1").userTask("task10").name("Restart Repair+complete").connectTo("gat1").moveToNode("egat1").connectTo("egat0").moveToNode("egat0").userTask("task11").name("Archive Repair+complete").endEvent("end").done();}}