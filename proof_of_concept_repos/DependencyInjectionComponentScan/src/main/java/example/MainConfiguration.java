package example;

import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;

@Configuration
@ComponentScan("example.beanConfiguration")
public class MainConfiguration {
    // empty
}