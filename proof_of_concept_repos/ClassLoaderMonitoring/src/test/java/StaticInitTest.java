import org.junit.Test;
import static org.junit.Assert.*;

public class StaticInitTest {

    @Test
    public void testStaticInitLoadingDetection() {
        try {
            // load the class and initialize statics without calling the constructor
            Class.forName("StaticInitClass");

            // this fails if the staticInitClass changed the truth value
            assertTrue(BaseClass.thisIsTrue);
        } catch (ClassNotFoundException e) {
            fail(e.getMessage());
        }
    }
}
