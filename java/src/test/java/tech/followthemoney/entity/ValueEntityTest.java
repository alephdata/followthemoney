package tech.followthemoney.entity;

import java.io.IOException;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import tech.followthemoney.model.Model;
import tech.followthemoney.model.PropertyType;
import tech.followthemoney.model.Schema;

public class ValueEntityTest {
    private static Model model;

    @BeforeAll
    public static void setUp() throws IOException {
        model = Model.loadDefault();
    }

    @Test
    public void testEntityBasics() {
        Schema schema = model.getSchema("Person");
        ValueEntity entity = new ValueEntity("harry", schema);
        entity.addValue(schema.getProperty("name"), "Harry Smith");
        entity.addValue(schema.getProperty("nationality"), "gb");

        assertTrue(entity.getValues(schema.getProperty("name")).contains("Harry Smith"));
        assertTrue(entity.getValues(schema.getProperty("nationality")).contains("gb"));

        PropertyType countryType = schema.getModel().getType(PropertyType.COUNTRY);
        assertTrue(entity.getTypeValues(countryType, false).contains("gb"));
        assertFalse(entity.getTypeValues(countryType, false).contains("de"));

        entity.addValue(schema.getProperty("name"), "Harry M. Smith");
        assertTrue(entity.getValues(schema.getProperty("name")).size() == 2);
    }
}
