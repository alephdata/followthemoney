package tech.followthemoney.model;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;

import com.fasterxml.jackson.databind.JsonNode;

import tech.followthemoney.exc.SchemaException;

public class Schema {
    private final Model model;
    private final String name;
    private final List<String> extendsNames;
    private final String label;
    private final String plural;
    private final List<String> featuredNames;
    private final List<String> requiredNames;
    private final List<String> captionNames;
    private final Set<Schema> schemata;
    private final Map<Schema, Schema> commonSchemata;
    private final Map<String, Property> properties;
    private Optional<Edge> edge;
    private Optional<TemporalExtent> temporalExtent;

    public Schema(Model model, String name, List<String> extendsSchemata, String label, String plural, List<String> featured, List<String> required, List<String> caption) {
        this.model = model;
        this.name = name.intern();
        this.extendsNames = ModelHelper.internStrings(extendsSchemata);
        this.label = label.length() == 0 ? this.name : label;
        this.plural = plural.length() == 0 ? this.label : plural;
        this.featuredNames = ModelHelper.internStrings(featured);
        this.requiredNames = ModelHelper.internStrings(required);
        this.captionNames = ModelHelper.internStrings(caption);
        this.schemata = new HashSet<>();
        this.properties = new HashMap<>();
        this.commonSchemata = new HashMap<>();
        this.edge = Optional.empty();
        this.temporalExtent = Optional.empty();
    }

    protected void buildHierarchy() {
        for (Schema schema : getSchemata()) {
            for (Property property : schema.getProperties()) {
                if (!properties.containsKey(property.getName())) {
                    properties.put(property.getName(), property);
                }
            }
        }
    }

    public Model getModel() {
        return model;
    }

    /**
     * Get a list of Schema objects that this schema extends from.
     * 
     * @return A list of Schema objects representing the schemas that this schema extends.
     *         The list is constructed based on the schema names stored in extendsNames.
     *         Returns an empty list if this schema doesn't extend any other schemas.
     */
    public List<Schema> getExtends() {
        List<Schema> extendsSchemata = new ArrayList<>();
        for (String schemaName : extendsNames) {
            extendsSchemata.add(model.getSchema(schemaName));
        }
        return extendsSchemata;
    }

    public Set<Schema> getSchemata() {
        if (schemata.isEmpty()) {
            schemata.add(this);
            for (Schema schema : getExtends()) {
                schemata.addAll(schema.getSchemata());
            }
        }
        return schemata;
    }

    public boolean isA(Schema schema) {
        if (schema == null) {
            return false;
        }
        if (schema == this) {
            return true;
        }
        return getSchemata().contains(schema);
    }

    public Schema computeCommonWith(Schema other) throws SchemaException {
        if (this.isA(other)) {
            return this;
        } 
        if (other.isA(this)) {
            return other;
        }
        for (Schema third : getModel().getSchemata().values()) {
            if (third.isA(this) && third.isA(other)) {
                return third;
            }
        }
        throw new SchemaException("No common schema found: " + this.getName() + " and " + other.getName());
    }

    @SuppressWarnings("StringEquality")
    public Schema commonWith(Schema other) throws SchemaException {
        if (other == null || other.name == this.name) {
            return this;
        }
        if (!commonSchemata.containsKey(other)) {
            commonSchemata.put(other, computeCommonWith(other));
        }
        return commonSchemata.get(other);
    }

    public String getName() {
        return name;
    }

    public String getLabel() {
        return label;
    }

    public String getPlural() {
        return plural;
    }

    protected void addProperty(Property property) {
        properties.put(property.getName(), property);
    }

    public Property getProperty(String name) {
        return properties.get(name);
    }

    public boolean hasProperty(String name) {
        return properties.containsKey(name);
    }

    public List<Property> getProperties() {
        return new ArrayList<>(properties.values());
    }

    public List<Property> getFeaturedProperties() {
        List<Property> featuredProperties = new ArrayList<>();
        for (String propertyName : featuredNames) {
            featuredProperties.add(properties.get(propertyName));
        }
        return featuredProperties;
    }

    public List<Property> getRequiredProperties() {
        List<Property> requiredProperties = new ArrayList<>();
        for (String propertyName : requiredNames) {
            requiredProperties.add(properties.get(propertyName));
        }
        return requiredProperties;
    }

    public List<Property> getCaptionProperties() {
        List<Property> captionProperties = new ArrayList<>();
        for (String propertyName : captionNames) {
            captionProperties.add(properties.get(propertyName));
        }
        return captionProperties;
    }

    public Optional<Edge> getEdge() {
        return edge;
    }

    public boolean isEdge() {
        return edge.isPresent();
    }

    public Optional<TemporalExtent> getTemporalExtent() {
        return temporalExtent;
    }

    public boolean isTemporal() {
        return temporalExtent.isPresent();
    }

    @Override
    public String toString() {
        return name;
    }

    @Override
    public int hashCode() {
        return Objects.hash(name);
    }

    @Override
    public boolean equals(Object obj) {
        if (obj == this) return true;
        if (obj == null || !(obj instanceof Schema)) {
            return false;
        }
        Schema other = (Schema) obj;
        return name.equals(other.name);
    }

    public static Schema fromJson(Model model, String name, JsonNode node) {
        Schema schema = new Schema(model, name,
            ModelHelper.getJsonStringArray(node, "extends"),
            node.get("label").asText(),
            node.get("plural").asText(),
            ModelHelper.getJsonStringArray(node, "featured"),
            ModelHelper.getJsonStringArray(node, "required"),
            ModelHelper.getJsonStringArray(node, "caption"));

        Optional<Edge> edge = node.has("edge") ? Optional.of(Edge.fromJson(schema, node.get("edge"))) : Optional.empty();
        schema.edge = edge;
        Optional<TemporalExtent> temporalExtent = node.has("temporalExtent") ? Optional.of(TemporalExtent.fromJson(schema, node.get("temporalExtent"))) : Optional.empty();
        schema.temporalExtent = temporalExtent;

        JsonNode propertiesNode = node.get("properties");
        Iterator<String> it = propertiesNode.fieldNames();
        while (it.hasNext()) {
            String propertyName = it.next();
            JsonNode propertyNode = propertiesNode.get(propertyName);
            Property property = Property.fromJson(schema, propertyName, propertyNode);
            schema.addProperty(property);
        }
        return schema;
    }
}
