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
        return Bpmn.createProcess().startEvent("start").userTask("task0").name("Register+complete").userTask("task1").name("Analyze Defect+start").exclusiveGateway("gat0").exclusiveGateway("gat1").exclusiveGateway("gat2").exclusiveGateway("gat3").exclusiveGateway("gat4").exclusiveGateway("gat5").exclusiveGateway("gat6").exclusiveGateway("gat7").endEvent("end").moveToNode("gat7").moveToNode("gat6").moveToNode("gat5").moveToNode("gat4").moveToNode("gat3").userTask("task2").name("Analyze Defect+complete").userTask("task3").name("Inform User+complete").exclusiveGateway("gat8").userTask("task4").name("Repair (Simple)+start").exclusiveGateway("gat9").moveToNode("gat9").moveToNode("gat9").moveToNode("gat9").moveToNode("gat8").userTask("task5").name("Repair (Complex)+start").exclusiveGateway("gat10").moveToNode("gat10").moveToNode("gat10").moveToNode("gat2").userTask("task6").name("Analyze Defect+complete").userTask("task7").name("Repair (Complex)+start").exclusiveGateway("gat11").moveToNode("gat11").moveToNode("gat1").userTask("task8").name("Analyze Defect+complete").userTask("task9").name("Repair (Simple)+start").exclusiveGateway("gat12").moveToNode("gat12").moveToNode("gat12").userTask("task10").name("Repair (Simple)+complete").moveToNode("gat0").moveToNode("gat7").connectTo("end").moveToNode("gat6").connectTo("end").moveToNode("gat5").connectTo("end").moveToNode("gat4").connectTo("end").moveToNode("gat9").connectTo("end").moveToNode("gat9").connectTo("end").moveToNode("gat9").connectTo("end").moveToNode("gat9").connectTo("end").moveToNode("gat10").connectTo("end").moveToNode("gat10").connectTo("end").moveToNode("gat10").connectTo("end").moveToNode("gat11").connectTo("end").moveToNode("gat11").connectTo("end").moveToNode("gat12").connectTo("end").moveToNode("gat12").connectTo("end").moveToNode("task10").connectTo("end").moveToNode("gat0").connectTo("end").done();}}