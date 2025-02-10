package tech.followthemoney.model;

import java.io.IOException;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.Test;

public class ModelTest {
    @Test
    public void testLoadDefault() throws IOException {
        Model model = Model.loadDefault();
        assertNotNull(model);
        assertFalse(model.getSchemata().isEmpty());
        assertFalse(model.getTypes().isEmpty());
        
        // Test getting a known schema type
        Schema legalEntity = model.getSchema("LegalEntity");
        Schema person = model.getSchema("Person");
        assertNotNull(person);
        assertEquals("Person", person.getName());
        assertTrue(person.getExtends().size() == 1);
        assertTrue(person.isA(legalEntity));
        assertTrue(person.isA(person));
        assertFalse(person.isEdge());
        assertTrue(person.isTemporal());
        assertEquals(person.getTemporalExtent().get().getStartProperties().get(0), person.getProperty("birthDate"));
        assertEquals(person.getTemporalExtent().get().getEndProperties().get(0), person.getProperty("deathDate"));
        
        // Test getting a known property type
        PropertyType type = model.getType("name");
        assertNotNull(type);
        assertEquals("name", type.getName());
        assertEquals(true, type.isName());

        // Test getting a known property
        Property property = person.getProperty("name");
        assertNotNull(property);
        assertEquals("name", property.getName());
        assertEquals("Thing:name", property.getQName());
        assertEquals("Name", property.getLabel());
        assertEquals(type, property.getType());

        Schema ownership = model.getSchema("Ownership");
        Property owner = ownership.getProperty("owner");
        assertTrue(owner.getType().isEntity());
        assertTrue(owner.getRange().isPresent());
        assertTrue(owner.getRange().get() == legalEntity);

        assertTrue(ownership.isEdge());
        assertEquals(ownership.getEdge().get().getSourceProperty(), owner);
        // FIXME: is this bad in the actual schema? 
        // Property startDate = ownership.getProperty("startDate");
        // assertTrue(ownership.isTemporal());
        // assertEquals(ownership.getTemporalExtent().get().getStartProperties().getFirst(), startDate);
    }
}
