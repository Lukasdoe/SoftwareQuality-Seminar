import com.google.inject.Guice;
import com.google.inject.Inject;
import org.junit.Test;

import static org.junit.Assert.assertTrue;

public class BaseTest {

    private static class InjectionHelper {
        @Inject
        public InjectedInterface injectedSupplier;
    }

    @Test
    public void testInjectedSupplier() {
        assertTrue(Guice.createInjector().getInstance(InjectionHelper.class).injectedSupplier.getTrue());
    }
}
