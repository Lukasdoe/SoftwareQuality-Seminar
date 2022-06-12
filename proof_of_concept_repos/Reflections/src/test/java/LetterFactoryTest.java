import org.junit.Test;
import static org.junit.Assert.*;

public class LetterFactoryTest {
    @Test
    public void testLetterFactoryA() {
        assertEquals('A', LetterFactory.createLetterInstance('A').getLetter());
    }

    @Test
    public void testLetterFactoryB() {
        assertEquals('B', LetterFactory.createLetterInstance('B').getLetter());
    }
}
