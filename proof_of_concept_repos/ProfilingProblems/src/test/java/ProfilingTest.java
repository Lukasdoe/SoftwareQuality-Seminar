import org.junit.Test;

import java.lang.reflect.AnnotatedType;

import static org.junit.Assert.*;

public class ProfilingTest {
    @Test
    public void testAdditionalInnerClasses() {
        assertEquals(2, ExampleClass.class.getDeclaredClasses().length);
        assertEquals(0, ExampleClass.class.getDeclaredFields().length);

        assertEquals(2, ExampleClass.class.getClasses().length);
        assertEquals(0, ExampleClass.class.getFields().length);
    }

    @Test
    public void testGetAnnotatedInterfaces() {
        assertTrue(ExampleClass.class.getAnnotatedInterfaces() instanceof AnnotatedType[]);
        assertEquals(0, ExampleClass.class.getAnnotatedInterfaces().length);
    }

    @Test
    public void testGetAnnotatedSuperclass() {
        assertNotNull(ExampleClass.class.getAnnotatedSuperclass());
    }

    @Test
    public void testToGenericString() {
        assertEquals("public class ExampleClass", ExampleClass.class.toGenericString());
    }
}