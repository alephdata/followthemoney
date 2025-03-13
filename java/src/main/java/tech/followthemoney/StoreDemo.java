package tech.followthemoney;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

import tech.followthemoney.entity.ValueEntity;
import tech.followthemoney.exc.SchemaException;
import tech.followthemoney.model.Model;
import tech.followthemoney.store.MemoryView;

public class StoreDemo {
    public static void main(String[] args) {
        String path = "/Users/pudo/Data/entities.ftm.json";
        try {
            BufferedReader reader = new BufferedReader(new FileReader(path));
            Model model = Model.loadDefault();
            MemoryView<ValueEntity> view = MemoryView.fromJsonReader(model, reader);
            System.out.println(view);
            Thread.sleep(600000);
        } catch (IOException | SchemaException | InterruptedException e) {
            e.printStackTrace();
        }
        
    }
}
