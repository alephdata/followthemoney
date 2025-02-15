package tech.followthemoney.store;

import java.util.Optional;
import java.util.stream.Stream;

import org.apache.commons.lang3.tuple.Pair;

import tech.followthemoney.entity.Entity;
import tech.followthemoney.model.Model;
import tech.followthemoney.model.PropertyType;

public abstract class View<E extends Entity> {
    public abstract boolean hasEntity(String id);
    public abstract Optional<E> getEntity(String id);
    public abstract Stream<E> allEntities();
    public abstract Stream<Adjacency<E>> getInverted(String id);

    public Stream<Adjacency<E>> getOutbound(E entity) {
        Model model = entity.getSchema().getModel();
        PropertyType entityType = model.getType(PropertyType.ENTITY);

        return entity.getDefinedProperties().stream()
            .filter(property -> property.getType().equals(entityType))
            .map(property -> entity.getValues(property).stream().map((value) -> Pair.of(property, getEntity(value))))
            .flatMap(mapper -> mapper)
            .filter(pair -> pair.getRight().isPresent())
            .map(pair -> new Adjacency<>(pair.getLeft(), pair.getRight().get()));
    }

    public Stream<Adjacency<E>> getAdjacent(E entity) {
        Stream<Adjacency<E>> directLinks = getOutbound(entity);
        if (entity.getId() != null) {
            return Stream.concat(directLinks, getInverted(entity.getId()));
        }
        return directLinks;
    }

    
}
