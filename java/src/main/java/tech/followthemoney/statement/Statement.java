package tech.followthemoney.statement;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Objects;
import java.util.Optional;

import tech.followthemoney.model.ModelHelper;
import tech.followthemoney.model.Property;
import tech.followthemoney.model.Schema;

public class Statement {
    // private static final String DEFAULT_LANG = "und";
    private static final String EMPTY = "".intern();
    public static final String ID_PROP = "id".intern();

    private final String id;
    private final String entityId;
    private final String canonicalId;
    private final Schema schema;
    private final String propertyName;
    private final String dataset;
    private final String value;
    private final String lang;
    private final String originalValue;
    private final boolean external;
    private final long firstSeen;
    private final long lastSeen;

    public Statement(String id, String entityId, String canonicalId, Schema schema, String propertyName, String dataset, String value, String lang, String originalValue, boolean external, long firstSeen, long lastSeen) {
        // this.id = parseId(id);
        this.id = id;
        this.entityId = entityId;
        this.canonicalId = canonicalId == null || canonicalId.equals(entityId) || canonicalId.length() == 0 ? EMPTY : canonicalId;
        this.schema = schema;
        this.propertyName = propertyName; // .intern();
        this.dataset = dataset; // .intern();
        // Property property = schema.getProperty(propertyName);
        // this.value = (property != null && property.isEnum()) ? value.intern() : value;
        this.value = value;
        this.lang = lang == null || lang.length() == 0 ? EMPTY : lang;
        this.originalValue = originalValue == null || originalValue.length() == 0 ? EMPTY : originalValue;
        this.external = external;
        this.firstSeen = firstSeen;
        this.lastSeen = lastSeen;
    }

    public String getId() {
        // return id.toString(16);
        return id;
    }

    public String getEntityId() {
        return entityId;
    }

    @SuppressWarnings("StringEquality")
    public String getCanonicalId() {
        return canonicalId == EMPTY ? entityId : canonicalId;
    }

    public Schema getSchema() {
        return schema;
    }

    public Optional<Property> getProperty() {
        Property property = schema.getProperty(propertyName);
        if (property == null) {
            return Optional.empty();
        }
        return Optional.of(property);
    }

    public String getPropertyName() {
        return propertyName;
    }

    public String getDatasetName() {
        return dataset;
    }

    public String getValue() {
        return value;
    }

    public String getLang() {
        return lang;
    }

    public String getOriginalValue() {
        return originalValue;
    }

    public boolean isExternal() {
        return external;
    }

    public long getFirstSeen() {
        return firstSeen;
    }

    public long getLastSeen() {
        return lastSeen;
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }

    @Override
    public boolean equals(Object obj) {
        if (obj == null || !(obj instanceof Statement)) {
            return false;
        }
        Statement other = (Statement) obj;
        return id.equals(other.id);
    }

    @Override
    public String toString() {
        return String.format("Statement(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", id, entityId, canonicalId, schema, propertyName, dataset, value, lang, originalValue, external, firstSeen, lastSeen);
    }

    public Statement withCanonicalId(String canonicalId) {
        if (canonicalId.equals(getCanonicalId())) {
            return this;
        }
        return new Statement(this.getId(), entityId, canonicalId, schema, propertyName, dataset, value, lang, originalValue, external, firstSeen, lastSeen);
    }

    // public static BigInteger parseId(String id) {
    //     return new BigInteger(id, 16);
    // }

    public static String makeId(String dataset, String entityId, String propertyName, String value, boolean external) {
        byte[] sep = new byte[] { '.' };
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-1");
            digest.update(dataset.getBytes());
            digest.update(sep);
            digest.update(entityId.getBytes());
            digest.update(sep);
            digest.update(propertyName.getBytes());
            digest.update(sep);
            digest.update(value.getBytes());
            if (external) {
                digest.update(".ext".getBytes());
            }
            return ModelHelper.hexDigest(digest);
        } catch (NoSuchAlgorithmException e) {
            return null;
        }
    }

    public static String makeId(String dataset, String entityId, String propertyName, String value) {
        return makeId(dataset, entityId, propertyName, value, false);
    }
}
