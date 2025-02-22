package tech.followthemoney.store;

import java.util.Optional;

import tech.followthemoney.entity.Entity;
import tech.followthemoney.model.Model;
import tech.followthemoney.model.Property;
import tech.followthemoney.model.PropertyType;

public class Adjacency<E extends Entity> {
    private final Property property;
    private final E entity;

    public Adjacency(Property property, E entity) {
        this.property = property;
        this.entity = entity;
    }

    public Property getProperty() {
        return property;
    }

    public E getEntity() {
        return entity;
    }

    public static <T extends Entity> Adjacency<T> ofInverse(String entityId, T entity) {
        Model model = entity.getSchema().getModel();
        PropertyType entityType = model.getType(PropertyType.ENTITY);
        Optional<Property> prop = entity.getDefinedProperties().stream()
            .filter(property -> property.getType().equals(entityType))
            .filter(property -> entity.getValues(property).contains(entityId))
            .findFirst();
        return new Adjacency<>(prop.get(), entity);
    }
}
