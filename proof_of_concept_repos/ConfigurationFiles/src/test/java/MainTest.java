import org.junit.Test;
import static org.junit.Assert.*;
import java.io.IOException;

public class MainTest {

    @Test
    public void testTestedMethod() {
        try {
            System.out.println( new Main().testedMethod());
            assertEquals("testValue=Test1", new Main().testedMethod());
        } catch (IOException e){
            System.out.println(e);
            fail(e.getMessage());
        }
    }
}