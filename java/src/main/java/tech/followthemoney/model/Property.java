package tech.followthemoney.model;

import java.util.Objects;
import java.util.Optional;

import com.fasterxml.jackson.databind.JsonNode;

public class Property {
    private final Schema schema;
    private final String name;
    private final String qname;
    private final String label;
    private final PropertyType type;
    private final int maxLength;
    private final boolean matchable;
    private final boolean stub;
    private final Optional<String> reverseName;
    private final Optional<String> rangeName;

    public Property(Schema schema, String name, PropertyType type, String label, int maxLength, boolean matchable, boolean stub, Optional<String> reverse, Optional<String> range) {
        this.schema = schema;
        this.name = name.intern();
        this.qname = schema.getName() + ":" + name;
        this.label = label.length() == 0 ? this.name : label;
        this.type = type;
        this.maxLength = maxLength;
        this.matchable = matchable;
        if (!type.isEntity() && stub) {
            throw new IllegalArgumentException("Only entity properties can be stubs: " + type.getName());
        }
        if (type.isEntity()) {
            if (reverse.isEmpty()) {
                throw new IllegalArgumentException("Entity properties must have a reverse property");
            }
            if (range.isEmpty()) {
                throw new IllegalArgumentException("Entity properties must have a range");
            }
        }
        this.stub = stub;
        this.reverseName = reverse;
        this.rangeName = range;
    }

    public PropertyType getType() {
        return type;
    }

    public String getName() {
        return name;
    }

    public String getQName() {
        return qname;
    }

    public String getLabel() {
        return label;
    }

    public int getMaxLength() {
        return maxLength;
    }

    public boolean isMatchable() {
        return matchable;
    }

    public boolean isStub() {
        return stub;
    }

    public boolean isEnum() {
        return type.isEnum();
    }

    public Optional<Schema> getRange() {
        if (!rangeName.isPresent()) {
            return Optional.empty();
        }
        return Optional.of(schema.getModel().getSchema(rangeName.get()));
    }

    public Optional<Property> getReverse() {
        Schema range = getRange().orElse(null);
        if (!reverseName.isPresent() || range == null) {
            return Optional.empty();
        }
        return Optional.of(range.getProperty(reverseName.get()));
    }

    @Override
    public String toString() {
        return qname;
    }

    @Override
    public int hashCode() {
        return Objects.hash(qname);
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Property other = (Property) obj;
        return qname.equals(other.qname);
    }

    public static Property fromJson(Schema schema, String name, JsonNode node) {
        PropertyType type = schema.getModel().getType(node.get("type").asText());
        String label = node.get("label").asText();
        int maxLength = node.has("maxLength") ? node.get("maxLength").asInt() : type.getMaxLength();
        boolean matchable = node.has("matchable") ? node.get("matchable").asBoolean() : type.isMatchable();
        boolean stub = node.has("stub") ? node.get("stub").asBoolean() : false;
        Optional<String> reverse = node.has("reverse") ? Optional.of(node.get("reverse").asText().intern()) : Optional.empty();
        Optional<String> range = node.has("range") ? Optional.of(node.get("range").asText().intern()) : Optional.empty();
        return new Property(schema, name, type, label, maxLength, matchable, stub, reverse, range);
    }
}
