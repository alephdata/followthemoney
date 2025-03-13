package tech.followthemoney.store;

import java.io.BufferedReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Stream;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import tech.followthemoney.entity.Entity;
import tech.followthemoney.entity.ValueEntity;
import tech.followthemoney.exc.SchemaException;
import tech.followthemoney.model.Model;
import tech.followthemoney.model.PropertyType;

public class MemoryView<E extends Entity> extends View<E> {
    private final Map<String, E> entityMap;
    private final Map<String, Set<String>> inverted;

    public MemoryView() {
        this.entityMap = new HashMap<>();
        this.inverted = new HashMap<>();
    }

    protected void put(E entity) {
        PropertyType entityType = entity.getSchema().getModel().getType(PropertyType.ENTITY);
        for (String value : entity.getTypeValues(entityType, false)) {
            Set<String> entities = inverted.computeIfAbsent(value, k -> new HashSet<>());
            entities.add(entity.getId());
        }
        entityMap.put(entity.getId(), entity);
    }

    protected void delete(String entityId) {
        E entity = entityMap.remove(entityId);
        if (entity != null) {
            PropertyType entityType = entity.getSchema().getModel().getType(PropertyType.ENTITY);
            for (String value : entity.getTypeValues(entityType, false)) {
                if (inverted.containsKey(value)) {
                    Set<String> entities = inverted.get(value);
                    entities.remove(entityId);
                    if (entities.isEmpty()) {
                        inverted.remove(value);
                    }
                }
            }
        }
    }

    protected void clear() {
        entityMap.clear();
        inverted.clear();
    }

    @Override
    public boolean hasEntity(String entityId) {
        return entityMap.containsKey(entityId);
    }

    @Override
    public Optional<E> getEntity(String entityId) {
        E entity = entityMap.get(entityId);
        if (entity == null) {
            return Optional.empty();
        }
        return Optional.of(entity);
    }

    @Override
    public Stream<E> allEntities() {
        return entityMap.values().stream();
    }

    @Override
    public Stream<Adjacency<E>> getInverted(String entityId) {
        if (!inverted.containsKey(entityId)) {
            return Stream.empty();
        }
        return inverted.get(entityId).stream()
            .map(id -> Adjacency.ofInverse(entityId, entityMap.get(id)))
            .filter(adj -> adj.getEntity() != null && adj.getProperty() != null);
    }

    @Override
    public void close() {
        clear();
    }

    public static MemoryView<ValueEntity> fromJsonReader(Model model, BufferedReader reader) throws IOException, SchemaException {
        MemoryView<ValueEntity> view = new MemoryView<>();
        ObjectMapper mapper = new ObjectMapper();
        String line;
        while ((line = reader.readLine()) != null) {
            JsonNode node = mapper.readTree(line);
            view.put(ValueEntity.fromJson(model, node));
        }
        return view;
    }
}
