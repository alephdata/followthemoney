package tech.followthemoney.model;

import java.util.Map;
import java.util.Objects;
import java.util.Optional;

import com.fasterxml.jackson.databind.JsonNode;

public class PropertyType {
    private final String name;
    private final String label;
    private final String plural;
    private final String description;
    private final Optional<String> group;
    private final int maxLength;
    private final boolean matchable;
    private final boolean pivot;
    private final Optional<Map<String, String>> values;
    private final boolean enumType;

    public static String ENTITY = "entity".intern();
    public static String NAME = "name".intern();
    public static String COUNTRY = "country".intern();
    public static String IDENTIFIER = "identifier".intern();

    public PropertyType(String name, String label, String plural, String description, Optional<String> group, int maxLength, boolean matchable, boolean pivot, Optional<Map<String, String>> values) {
        if (name == null) {
            throw new IllegalArgumentException("Property type name cannot be null");
        }
        this.name = name.intern();
        this.label = label.length() == 0 ? this.name : label;
        this.plural = plural.length() == 0 ? this.label : plural;
        this.description = description;
        this.group = group;
        this.maxLength = maxLength;
        this.matchable = matchable;
        this.pivot = pivot;
        this.values = values;
        this.values.ifPresent(v -> v.forEach((k, v1) -> k.intern()));
        this.enumType = this.values.isPresent() && !this.values.get().isEmpty();
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

    public String getDescription() {
        return description;
    }

    public int getMaxLength() {
        return maxLength;
    }

    public Optional<String> getGroup() {
        return group;
    }

    public boolean isMatchable() {
        return matchable;
    }

    public boolean isPivot() {
        return pivot;
    }

    public boolean isEntity() {
        return name.equals(ENTITY);
    }

    public boolean isName() {
        return name.equals(NAME);
    }

    public boolean isIdentifier() {
        return name.equals(IDENTIFIER);
    }

    public Optional<Map<String, String>> getValues() {
        return values;
    }

    public boolean isEnum() {
        return enumType;
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
        if (this == obj) return true;
        if (obj == null || !(obj instanceof PropertyType)) {
            return false;
        }
        PropertyType other = (PropertyType) obj;
        return name.equals(other.name);
    }

    public static PropertyType fromJson(String name, JsonNode node) {
        Optional<String> group = node.has("group") ? Optional.of(node.get("group").asText()) : Optional.empty();
        Optional<Map<String, String>> values = node.has("values") ? Optional.of(ModelHelper.getJsonStringMap(node, "values")) : Optional.empty();
        return new PropertyType(name,
            node.get("label").asText(),
            node.get("plural").asText(),
            node.get("description").asText(),
            group,
            node.get("maxLength").asInt(),
            node.has("matchable") ? node.get("matchable").asBoolean() : false,
            node.has("pivot") ? node.get("pivot").asBoolean() : false,
            values);
    }
}
