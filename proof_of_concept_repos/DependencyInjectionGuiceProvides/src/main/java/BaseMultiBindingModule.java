import com.google.inject.AbstractModule;
import com.google.inject.Provides;

public class BaseMultiBindingModule extends AbstractModule {
    // this first legal binding can also be done using the configure() method.
    @Provides
    InjectedInterface impl1() {
        return () -> true;
    }

//    @Provides
//    InjectedInterface impl2() {
//        return () -> false;
//    }
}
