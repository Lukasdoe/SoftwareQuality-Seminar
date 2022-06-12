import com.google.inject.Guice;
import com.google.inject.Inject;
import com.google.inject.Injector;
import org.junit.Test;

import java.util.Collection;
import java.util.Set;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

public class BaseTest {

    private static class InjectionHelper {
        @Inject
        public InjectedInterface injectedSuppliers;
    }

    @Test
    public void testInjectedSupplier() {
        Injector injector = Guice.createInjector(new BaseMultiBindingModule());
        assertTrue(injector.getInstance(InjectionHelper.class).injectedSuppliers.getTrue());
    }
}
