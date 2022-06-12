package example;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit4.SpringRunner;

import java.util.function.BooleanSupplier;

import static junit.framework.TestCase.assertTrue;

@RunWith(SpringRunner.class)
@SpringBootTest(classes = MainSpringApplicationClass.class)
public class DependencyInjectionTests {
    @Autowired
    private BooleanSupplier truthValue;

    @Test
    public void testDeps() {
        assertTrue(truthValue.getAsBoolean());
    }
}
