import org.junit.Test;
import static org.junit.Assert.*;

public class DynamicDispatchTest {

    @Test
    public void testDispatch() {
        assertTrue(new ChildClass().getTrue());
    }
}