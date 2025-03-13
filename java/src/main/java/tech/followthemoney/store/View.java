package tech.followthemoney.store;

import java.util.Optional;
import java.util.stream.Stream;

import org.apache.commons.lang3.tuple.Pair;

import tech.followthemoney.entity.Entity;
import tech.followthemoney.exc.ViewException;

public abstract class View<E extends Entity> {
    public abstract boolean hasEntity(String id) throws ViewException;
    public abstract Optional<E> getEntity(String id) throws ViewException;
    public abstract Stream<E> allEntities() throws ViewException;
    public abstract Stream<Adjacency<E>> getInverted(String id) throws ViewException;

    public Stream<Adjacency<E>> getOutbound(E entity) throws ViewException {
        return entity.getDefinedProperties().stream()
            .filter(property -> property.getType().isEntity())
            .map(property -> entity.getValues(property).stream().map((value) -> {
                try {
                    return Pair.of(property, getEntity(value));
                } catch (ViewException e) {
                    return null;
                }
            }))
            .flatMap(mapper -> mapper)
            .filter(pair -> pair != null && pair.getRight().isPresent())
            .map(pair -> new Adjacency<>(pair.getLeft(), pair.getRight().get()));
    }

    public Stream<Adjacency<E>> getAdjacent(E entity) throws ViewException {
        Stream<Adjacency<E>> directLinks = getOutbound(entity);
        if (entity.getId() != null) {
            return Stream.concat(directLinks, getInverted(entity.getId()));
        }
        return directLinks;
    }

    public void close() throws ViewException {
    }
}
