import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Properties;
import java.util.stream.Collectors;

public class Main {
    static final String CONFIG_PATH = "test.conf";


    public String testedMethod() throws IOException {
        Properties prop = new Properties();
        prop.load(getClass().getClassLoader().getResourceAsStream(CONFIG_PATH));
        return prop.getProperty("testValue");
    }
}
