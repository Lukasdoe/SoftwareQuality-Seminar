package example.beanConfiguration;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.function.BooleanSupplier;

@Configuration
public class BeanConfig1 {
    @Bean
    public BooleanSupplier truthValue() {
        return () -> true;
    }
}
