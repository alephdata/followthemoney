package tech.followthemoney.entity;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

import tech.followthemoney.exc.SchemaException;
import tech.followthemoney.model.Model;
import tech.followthemoney.model.ModelHelper;
import tech.followthemoney.model.Property;
import tech.followthemoney.model.Schema;

public class ValueEntity extends Entity {
    private final static Logger log = LoggerFactory.getLogger(ValueEntity.class);
    
    private Set<String> datasets;
    private Set<String> referents;
    private long firstSeen;
    private long lastSeen;
    private long lastChange;
    private final Map<Property, List<String>> properties;

    public ValueEntity(String id, Schema schema, Map<Property, List<String>> properties) {
        super(id, schema);
        this.properties = properties;
    }

    public ValueEntity(String id, Schema schema) {
        this(id, schema, new HashMap<>());
    }

    @Override
    protected String pickCaption() {
        for (Property prop : schema.getCaptionProperties()) {
            if (properties.containsKey(prop)) {
                // Put in the logic to pick the display name
                return properties.get(prop).get(0);
            }
        }
        return schema.getLabel();
    }

    @Override
    public Set<String> getDatasets() {
        return datasets;
    }

    public void setDatasets(Set<String> datasets) {
        this.datasets = datasets;
    }

    @Override
    public Set<String> getReferents() {
        return referents;
    }

    public void setReferents(Set<String> referents) {
        this.referents = referents;
    }

    @Override
    public long getFirstSeen() {
        return firstSeen;
    }

    public void setFirstSeen(long firstSeen) {
        this.firstSeen = firstSeen;
    }

    @Override
    public long getLastSeen() {
        return lastSeen;
    }

    public void setLastSeen(long lastSeen) {
        this.lastSeen = lastSeen;
    }

    @Override
    public long getLastChange() {
        return lastChange;
    }

    public void setLastChange(long lastChange) {
        this.lastChange = lastChange;
    }

    public boolean has(Property property) {
        return properties.containsKey(property);
    }

    @Override
    public List<String> getValues(Property property) {
        if (!properties.containsKey(property)) {
            return new ArrayList<>();
        }
        return properties.get(property);
    }

    public void addValue(String propertyName, String value) throws SchemaException {
        Property property = schema.getProperty(propertyName);
        if (property == null) {
            throw new SchemaException("Invalid property: " + propertyName);
        }
        addValue(property, value);
    }

    public void addValue(Property property, String value) {
        if (property == null) {
            return;
        }
        if (property.isEnum()) {
            value = value.intern();
        }
        List<String> values = properties.getOrDefault(property, new ArrayList<>());
        if (!values.contains(value)) {
            values.add(value);
        }
        properties.put(property, values);
    }

    @Override
    public Set<Property> getDefinedProperties() {
        return properties.keySet();
    }

    @Override
    public JsonNode toValueJson() {
        ObjectMapper mapper = new ObjectMapper();
        ObjectNode node = mapper.createObjectNode();
        if (this.id != null) {
            node.put("id", this.id);
        }
        node.put("schema", schema.getName());
        node.put("caption", getCaption());
        if (!properties.isEmpty()) {
            ObjectNode propsNode = node.putObject("properties");
            for (Map.Entry<Property, List<String>> entry : properties.entrySet()) {
                Property property = entry.getKey();
                ModelHelper.putJsonStringIterable(propsNode, property.getName(), entry.getValue());
            }
        }
        if (datasets != null) {
            ModelHelper.putJsonStringIterable(node, "datasets", datasets);
        }
        if (referents != null && !referents.isEmpty()) {
            ModelHelper.putJsonStringIterable(node, "referents", referents);
        }
        if (firstSeen > 0) {
            node.put("first_seen", ModelHelper.toTimeStamp(firstSeen));
        }
        if (lastSeen > 0) {
            node.put("last_seen", ModelHelper.toTimeStamp(lastSeen));
        }
        if (lastChange > 0) {
            node.put("last_change", ModelHelper.toTimeStamp(lastChange));
        }
        return node;
    }

    public static ValueEntity fromJson(Model model, JsonNode node) throws SchemaException {
        String entityId = node.get("id").asText();
        String schemaName = node.get("schema").asText();
        Schema schema = model.getSchema(schemaName);
        if (schema == null) {
            throw new SchemaException("Invalid schema: " + schemaName);
        }
        Map<Property, List<String>> properties = new HashMap<>();
        if (node.has("properties")) {
            JsonNode propsNode = node.get("properties");
            Iterator<String> it = propsNode.fieldNames();
            while (it.hasNext()) {
                String propertyName = it.next();
                Property property = schema.getProperty(propertyName);
                if (property == null) {
                    log.warn("Invalid property: {} (Entity: {}, Schema: {})", propertyName, entityId, schemaName);
                    continue;
                }
                List<String> values = ModelHelper.getJsonStringArray(propsNode, propertyName);
                if (property.isEnum()) {
                    values = ModelHelper.internStrings(values);
                }
                properties.put(property, values);
            }
        }
        ValueEntity entity = new ValueEntity(entityId, schema, properties);
        if (node.has("caption")) {
            entity.setCaption(node.get("caption").asText());
        }
        List<String> datasets = ModelHelper.internStrings(ModelHelper.getJsonStringArray(node, "datasets"));
        entity.setDatasets(new HashSet<>(datasets));
        entity.setReferents(ModelHelper.getJsonStringSet(node, "referents"));
        if (node.has("first_seen")) {
            long firstSeen = ModelHelper.fromTimeStamp(node.get("first_seen").asText());
            entity.setFirstSeen(firstSeen);
        }
        if (node.has("last_seen")) {
            long lastSeen = ModelHelper.fromTimeStamp(node.get("last_seen").asText());
            entity.setLastSeen(lastSeen);
        }
        if (node.has("last_change")) {
            long lastChange = ModelHelper.fromTimeStamp(node.get("last_change").asText());
            entity.setLastSeen(lastChange);
        }
        return entity;
    }
}
