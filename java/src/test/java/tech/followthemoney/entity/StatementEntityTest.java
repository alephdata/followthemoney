package tech.followthemoney.entity;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import tech.followthemoney.exc.SchemaException;
import tech.followthemoney.model.Model;
import tech.followthemoney.model.Schema;
import tech.followthemoney.statement.Statement;

public class StatementEntityTest {
    private static Model model;
    private static final String ENTITY_ID = "entity1";
    private static final String CANONICAL_ID = "canon1";
    private static final String DATASET = "test";

    @BeforeAll
    public static void setUp() throws IOException {
        model = Model.loadDefault();
    }
    
    @Test
    public void testEntityFromStatements() throws SchemaException {
        Schema schema = model.getSchema("Person");
        Statement stmt1 = new Statement("a1", ENTITY_ID, CANONICAL_ID, schema, 
            "name", DATASET, "Harry Smith", "", "", false, 100L, 200L);
        Statement stmt1b = new Statement("aaa", ENTITY_ID, CANONICAL_ID, schema, 
            "name", DATASET, "Harry M. Smith", "", "", false, 100L, 200L);
        Statement stmt2 = new Statement("aab", ENTITY_ID, CANONICAL_ID, schema, 
            "country", DATASET, "gb", null, null, false, 100L, 200L);
        Statement stmt3 = new Statement("deadbeef", ENTITY_ID, CANONICAL_ID, schema, 
            "birthDate", DATASET, "1980-01-15", null, null, false, 100L, 200L);
        List<Statement> stmts = new ArrayList<>();
        stmts.add(stmt1);
        stmts.add(stmt1b);
        stmts.add(stmt2);
        StatementEntity entity = StatementEntity.fromStatements(stmts);
        assertTrue(entity.has(schema.getProperty("name")));
        assertEquals(entity.getStatements(schema.getProperty("name")).size(), 2);
        assertFalse(entity.has(schema.getProperty("birthDate")));
        entity.addStatement(stmt3);
        assertTrue(entity.has(schema.getProperty("birthDate")));
    }
}
