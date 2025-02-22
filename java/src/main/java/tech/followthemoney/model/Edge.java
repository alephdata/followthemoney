package tech.followthemoney.model;

import java.util.ArrayList;
import java.util.List;

import com.fasterxml.jackson.databind.JsonNode;

public class Edge {
    private final Schema schema;
    private final String source;
    private final String target;
    private final List<String> caption;
    private final String label;
    private final boolean directed;

    public Edge(Schema schema, String source, String target, List<String> caption, String label, boolean directed) {
        this.schema = schema;
        this.source = source;
        this.target = target;
        this.caption = caption;
        this.label = label;
        this.directed = directed;
    }

    public Property getSourceProperty() {
        return schema.getProperty(source);
    }

    public Property getTargetProperty() {
        return schema.getProperty(target);
    }

    public List<Property> getCaptionProperties() {
        List<Property> properties = new ArrayList<>();
        for (String name : caption) {
            properties.add(schema.getProperty(name));
        }
        return properties;
    }

    public String getLabel() {
        return label;
    }

    public boolean isDirected() {
        return directed;
    }

    public static Edge fromJson(Schema schema, JsonNode node) {
        String source = node.get("source").asText();
        String target = node.get("target").asText();
        List<String> caption = ModelHelper.getJsonStringArray(node, "caption");
        String label = node.has("label") ? node.get("label").asText() : schema.getLabel();
        boolean directed = node.has("directed") && node.get("directed").asBoolean();
        return new Edge(schema, source, target, caption, label, directed);
    }
}
