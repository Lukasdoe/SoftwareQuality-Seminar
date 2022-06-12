package example;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit4.SpringRunner;

import java.util.Collection;
import java.util.function.BooleanSupplier;

import static junit.framework.TestCase.assertTrue;

@RunWith(SpringRunner.class)
@SpringBootTest
public class DependencyInjectionTests {
    @Autowired
    private Collection<BooleanSupplier> truthSuppliers;

    @Test
    public void testSuppliers() {
        assertTrue(truthSuppliers.stream().allMatch(BooleanSupplier::getAsBoolean));
    }
}