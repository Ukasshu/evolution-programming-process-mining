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
        return Bpmn.createProcess().startEvent("start").userTask("task0").name("incoming claim+complete").exclusiveGateway("gat0").parallelGateway("gat1").userTask("task1").name("B check if sufficient information is available+start").userTask("task2").name("B register claim+complete").parallelGateway("egat1").moveToNode("gat1").userTask("task3").name("B check if sufficient information is available+complete").userTask("task4").name("B register claim+start").userTask("task5").name("determine likelihood of claim+start").userTask("task6").name("determine likelihood of claim+complete").connectTo("egat1").moveToNode("egat1").userTask("task7").name("S check if sufficient information is available+start").exclusiveGateway("gat2").userTask("task8").name("assess claim+start").exclusiveGateway("egat2").moveToNode("gat2").connectTo("egat2").moveToNode("egat2").exclusiveGateway("gat3").userTask("task9").name("close claim+start").exclusiveGateway("egat3").moveToNode("gat3").connectTo("egat3").moveToNode("egat3").userTask("task10").name("initiate payment+complete").userTask("task11").name("advise claimant on reimbursement+start").userTask("task12").name("end+complete").parallelGateway("gat4").userTask("task13").name("end+start").userTask("task14").name("determine likelihood of claim+start").userTask("task15").name("close claim+complete").parallelGateway("egat4").moveToNode("gat4").userTask("task16").name("advise claimant on reimbursement+start").userTask("task17").name("determine likelihood of claim+complete").userTask("task18").name("initiate payment+start").connectTo("egat4").moveToNode("egat4").userTask("task19").name("S register claim+complete").userTask("task20").name("advise claimant on reimbursement+complete").exclusiveGateway("gat5").endEvent("end").moveToNode("gat5").moveToNode("gat0").moveToNode("gat5").connectTo("end").moveToNode("gat0").connectTo("end").done();}}