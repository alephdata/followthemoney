package tech.followthemoney.entity;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.databind.JsonNode;

import tech.followthemoney.exc.SchemaException;
import tech.followthemoney.model.ModelHelper;
import tech.followthemoney.model.Property;
import tech.followthemoney.model.Schema;
import tech.followthemoney.statement.Statement;

public class StatementEntity extends Entity {
    private final static Logger log = LoggerFactory.getLogger(StatementEntity.class);
    private final Map<Property, List<Statement>> properties;
    private final List<Statement> idStatements;

    public StatementEntity(String id, Schema schema, Map<Property, List<Statement>> properties, List<Statement> idStatements) {
        super(id, schema);
        this.properties = properties;
        this.idStatements = idStatements;
    }

    @Override
    protected String pickCaption() {
        for (Property prop : schema.getCaptionProperties()) {
            if (properties.containsKey(prop)) {
                // Put in the logic to pick the display name
                return properties.get(prop).get(0).getValue();
            }
        }
        return schema.getLabel();
    }

    @Override
    public String getCaption() {
        return pickCaption();
    }

    @Override
    public Set<String> getDatasets() {
        Set<String> datasets = new HashSet<>();
        for (Statement statement : getAllStatements()) {
            datasets.add(statement.getDatasetName());
        }
        return datasets;
    }

    @Override
    public Set<String> getReferents() {
        Set<String> referents = new HashSet<>();
        for (Statement statement : getAllStatements()) {
            referents.add(statement.getEntityId());
        }
        referents.remove(id);
        return referents;
    }

    @Override
    public long getFirstSeen() {
        long firstSeen = Long.MAX_VALUE;
        for (Statement statement : getAllStatements()) {
            firstSeen = Math.min(firstSeen, statement.getFirstSeen());
        }
        return firstSeen;
    }

    @Override
    public long getLastSeen() {
        long lastSeen = 0;
        for (Statement statement : getAllStatements()) {
            lastSeen = Math.max(lastSeen, statement.getLastSeen());
        }
        return lastSeen;
    }

    @Override
    public long getLastChange() {
        long lastChange = 0;
        for (Statement statement : idStatements) {
            lastChange = Math.max(lastChange, statement.getFirstSeen());
        }
        return lastChange;
    }

    public void addStatement(Statement statement) throws SchemaException {
        if (!statement.getCanonicalId().equals(id)) {
            throw new IllegalArgumentException("Statement does not belong to this entity.");
        }
        Schema stmtSchema = statement.getSchema();
        if (stmtSchema != this.schema) {
            this.schema = this.schema.commonWith(stmtSchema);
        }
        String propName = statement.getPropertyName();
        if (propName == null || !schema.hasProperty(propName)) {
            String message = String.format("Statement property %s does not exist in schema %s.", propName, this.schema);
            throw new SchemaException(message);
        }
        Property prop = schema.getProperty(propName);
        properties.computeIfAbsent(prop, k -> new ArrayList<>()).add(statement);
    }

    public boolean has(Property property) {
        return properties.containsKey(property);
    }

    public List<Statement> popStatements(Property property) {
        return properties.remove(property);
    }

    public List<Statement> getStatements(Property property) {
        return properties.get(property);
    }

    @Override
    public List<String> getValues(Property property) {
        List<String> values = new ArrayList<>();
        if (!properties.containsKey(property)) {
            return values;
        }
        for (Statement statement : properties.get(property)) {
            String value = statement.getValue();
            if (!values.contains(value)) {
                values.add(value);
            }
        }
        return values;
    }

    public Map<Property, List<Statement>> getProperties() {
        return properties;
    }

    @Override
    public Set<Property> getDefinedProperties() {
        return properties.keySet();
    }

    public Statement computeChecksum(boolean external) {
        List<String> ids = new ArrayList<>();
        for (List<Statement> statements : properties.values()) {
            for (Statement stmt : statements) {
                ids.add(stmt.getId());
            }
        }
        ids.sort(String::compareTo);
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-1");
            for (String stmtId : ids) {
                digest.update(stmtId.getBytes());
            }
            String value = ModelHelper.hexDigest(digest);
            String dataset = getDatasets().iterator().next();
            String stmtId = Statement.makeId(dataset, id, Statement.ID_PROP, value, external);
            Instant instant = Instant.now();
            Statement idStatement = new Statement(stmtId, id, id, schema, Statement.ID_PROP, dataset, value, null, null, false, instant.getEpochSecond(), instant.getEpochSecond());
            idStatements.clear();
            idStatements.add(idStatement);
            return idStatement;
        } catch (NoSuchAlgorithmException e) {
            log.error("Failed to compute checksum: {}", e.getMessage());
            return null;
        }
    }

    public Iterable<Statement> getAllStatements() {
        List<Statement> allStatements = new ArrayList<>(idStatements);
        for (List<Statement> statements : properties.values()) {
            allStatements.addAll(statements);
        }
        return allStatements;
    }

    public boolean hasStatements() {
        return !properties.isEmpty();
    }

    public ValueEntity toValueEntity() {
        ValueEntity ve = new ValueEntity(id, schema);
        for (Property prop : properties.keySet()) {
            for (Statement stmt : properties.get(prop)) {
                ve.addValue(prop, stmt.getValue());
            }
        }
        ve.setCaption(getCaption());
        ve.setDatasets(getDatasets());
        ve.setReferents(getReferents());
        ve.setFirstSeen(getFirstSeen());
        ve.setLastSeen(getLastSeen());
        ve.setLastChange(getLastChange());
        return ve;
    }

    @Override
    public JsonNode toValueJson() {
        return toValueEntity().toValueJson();
    }

    public static StatementEntity fromStatements(String canonicalId, List<Statement> statements) throws SchemaException {
        if (statements.isEmpty()) {
            throw new IllegalArgumentException("Cannot create entity from empty list of statements.");
        }
        Schema schema = statements.get(0).getSchema();
        Map<Property, List<Statement>> properties = new HashMap<>();
        List<Statement> idStatements = new ArrayList<>();
        for (Statement statement : statements) {
            statement = statement.withCanonicalId(canonicalId);
            schema = schema.commonWith(statement.getSchema());
            if (statement.getPropertyName().equals(Statement.ID_PROP)) {
                idStatements.add(statement);
            } else {
                Property prop = schema.getProperty(statement.getPropertyName());
                if (prop != null) {
                    properties.computeIfAbsent(prop, k -> new ArrayList<>()).add(statement);
                } else {
                    log.warn("Property {} not found in schema {}", statement.getPropertyName(), schema.getName());
                }
            }
        }
        return new StatementEntity(canonicalId, schema, properties, idStatements);
    }

    public static StatementEntity fromStatements(List<Statement> statements) throws SchemaException {
        if (statements.isEmpty()) {
            throw new IllegalArgumentException("Cannot create entity from empty list of statements.");
        }
        String canonicalId = statements.get(0).getCanonicalId();
        return fromStatements(canonicalId, statements);
    }
}
