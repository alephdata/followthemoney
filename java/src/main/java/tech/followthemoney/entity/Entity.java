package tech.followthemoney.entity;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import tech.followthemoney.model.Property;
import tech.followthemoney.model.PropertyType;
import tech.followthemoney.model.Schema;

import com.fasterxml.jackson.databind.JsonNode;

public abstract class Entity {
    protected String id;
    protected Schema schema;
    protected String caption;

    public Entity(String id, Schema schema) {
        this.id = id;
        this.schema = schema;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public Schema getSchema() {
        return schema;
    }

    protected abstract String pickCaption();

    public String getCaption() {
        if (caption == null) {
            caption = pickCaption();
        }
        return caption;
    }
    
    public void setCaption(String caption) {
        this.caption = caption;
    }

    public abstract Set<String> getDatasets();
    public abstract Set<String> getReferents();
    public abstract long getFirstSeen();
    public abstract long getLastSeen();
    public abstract long getLastChange();

    public abstract List<String> getValues(Property property);
    public abstract Set<Property> getDefinedProperties();

    public List<String> getTypeValues(PropertyType type, boolean matchable) {
        Set<String> values = new HashSet<>();
        for (Property property : getDefinedProperties()) {
            if (property.getType() == type) {
                if (matchable && !property.isMatchable()) {
                    continue;
                }
                values.addAll(getValues(property));
            }
        }
        return new ArrayList<>(values);
    }

    public abstract JsonNode toValueJson();
}
