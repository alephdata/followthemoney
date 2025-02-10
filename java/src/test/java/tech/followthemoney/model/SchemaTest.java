package tech.followthemoney.model;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.Test;

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
}
