package example;

import org.junit.Test;
import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;

import java.util.Arrays;
import java.util.function.BooleanSupplier;

import static junit.framework.TestCase.assertTrue;

public class ComponentScanTest {
    @Test
    public void testComponentBean() {
        ApplicationContext context = new AnnotationConfigApplicationContext(MainConfiguration.class);
        BooleanSupplier simpleBoolean = context.getBean(BooleanSupplier.class);
        System.out.println(Arrays.toString(context.getBeanDefinitionNames()));
        assertTrue(simpleBoolean.getAsBoolean());
    }
}
