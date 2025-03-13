package tech.followthemoney.model;

import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

public class Model {
    private final Map<String, Schema> schemata = new HashMap<>();
    private final Map<String, PropertyType> types = new HashMap<>();

    public Map<String, Schema> getSchemata() {
        return schemata;
    }

    public void setSchemata(Map<String, Schema> schemata) {
        this.schemata.clear();
        this.schemata.putAll(schemata);
    }

    public Schema getSchema(String name) {
        return schemata.get(name);
    }

    public Map<String, PropertyType> getTypes() {
        return types;
    }

    public void setTypes(Map<String, PropertyType> types) {
        this.types.clear();
        this.types.putAll(types);
    }

    public PropertyType getType(String name) {
        return types.get(name);
    }

    public static Model fromJson(ObjectMapper mapper, JsonNode node) {
        Model model = new Model();
        JsonNode jsonTypes = node.get("types");
        Iterator<String> it = jsonTypes.fieldNames();
        while (it.hasNext()) {
            String typeName = it.next();
            JsonNode typeNode = jsonTypes.get(typeName);
            PropertyType propertyType = PropertyType.fromJson(typeName, typeNode);
            model.types.put(propertyType.getName(), propertyType);
        }
        JsonNode jsonSchemata = node.get("schemata");
        it = jsonSchemata.fieldNames();
        while (it.hasNext()) {
            String schemaName = it.next();
            JsonNode schemaNode = jsonSchemata.get(schemaName);
            Schema schema = Schema.fromJson(model, schemaName, schemaNode);
            model.schemata.put(schema.getName(), schema);
        }
        for (Schema schema : model.schemata.values()) {
            schema.buildHierarchy();
        }
        return model;
    }

    public static Model loadDefault() throws IOException {
        ObjectMapper mapper = new ObjectMapper();
        InputStream stream = Model.class.getResourceAsStream("/defaultModel.json");
        if (stream == null) {
            throw new IOException("Cannot find defaultModel.json");
        }
        JsonNode root = mapper.readTree(stream);
        Model model = Model.fromJson(mapper, root);
        return model;
    }
}
