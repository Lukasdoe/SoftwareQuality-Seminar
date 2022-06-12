import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.Test;

import static org.junit.Assert.*;
import static org.hamcrest.CoreMatchers.*;

public class MainApplicationClassTest {

    @Test
    public void returnCode() throws JsonProcessingException {
        ObjectMapper objectMapper = new ObjectMapper();
        assertThat(objectMapper.writeValueAsString(new Thread().getContextClassLoader()), is(not("{}")));
    }
}