package tech.followthemoney.model;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.Test;

import tech.followthemoney.exc.SchemaException;

public class SchemaTest {
    @Test
    public void testBasicSchemaProperties() {
        Model model = new Model();
        Map<String, PropertyType> types = model.getTypes();
        PropertyType stringType = new PropertyType("string", "String", "Strings", "....", Optional.empty(), 65000, false, false, Optional.empty());
        assertEquals(stringType.isMatchable(), false);
        types.put("string", stringType);
        PropertyType nameType = new PropertyType("name", "Name", "Names", "....", Optional.of("names"), 380, true, true, Optional.empty());
        types.put("name", nameType);
        Map<String, String> countryValues = Map.of("us", "United States", "gb", "United Kingdom");
        PropertyType countryType = new PropertyType("country", "Country", "Countries", "....", Optional.of("countries"), 7, true, true, Optional.of(countryValues));
        types.put(countryType.getName(), countryType);
        model.setTypes(types);

        List<String> extendsSchemata = new ArrayList<>();
        List<String> featured = Arrays.asList("name", "country");
        List<String> required = Arrays.asList("name");
        List<String> caption = Arrays.asList("name");
        
        Schema schema = new Schema(model, "Person", extendsSchemata, "Person", "People", 
                                   featured, required, caption);
        
        assertEquals("Person", schema.getName());
        assertEquals("Person", schema.getLabel());
        assertEquals("People", schema.getPlural());
        
        Property nameProperty = new Property(schema, "name", nameType, "Name", 65000, true, false, Optional.empty(), Optional.empty());
        Property countryProperty = new Property(schema, "country", countryType, "Country", 7, true, false, Optional.empty(), Optional.empty());
        
        schema.addProperty(nameProperty);
        schema.addProperty(countryProperty);
        
        assertEquals(2, schema.getProperties().size());
        assertEquals(nameProperty, schema.getProperty("name"));
        assertEquals(countryProperty, schema.getProperty("country"));
        
        assertFalse(nameProperty.isEnum());
        assertTrue(countryProperty.isEnum());
        
        assertEquals(2, schema.getFeaturedProperties().size());
        assertEquals(1, schema.getRequiredProperties().size());
        assertEquals(1, schema.getCaptionProperties().size());
        
        assertEquals(nameProperty, schema.getRequiredProperties().get(0));
        assertEquals(nameProperty, schema.getCaptionProperties().get(0));
    }

    @Test
    public void testSchemaLogic() throws SchemaException, IOException {
        Model model = Model.loadDefault();
        Schema person = model.getSchema("Person");
        Schema organization = model.getSchema("Organization");
        Schema address = model.getSchema("Address");
        Schema legalEntity = model.getSchema("LegalEntity");
        Schema asset = model.getSchema("Asset");
        Schema company = model.getSchema("Company");

        assertTrue(person.isA(person));
        assertTrue(organization.isA(organization));
        assertTrue(address.isA(address));
        assertTrue(legalEntity.isA(legalEntity));
        assertTrue(person.isA(legalEntity));
        assertTrue(organization.isA(legalEntity));

        assertEquals(person.commonWith(person), person);
        assertEquals(legalEntity.commonWith(person), person);
        assertEquals(person.commonWith(legalEntity), person);
        assertEquals(legalEntity.commonWith(company), company);
        assertEquals(legalEntity.commonWith(asset), company);

        SchemaException exception = assertThrows(SchemaException.class, () -> person.commonWith(asset));
        assertTrue(exception.getMessage().contains("No common schema found: Person and Asset"));
            exception = assertThrows(SchemaException.class, () -> person.commonWith(address));
        assertTrue(exception.getMessage().contains("No common schema found: Person and Address"));
    }
}
