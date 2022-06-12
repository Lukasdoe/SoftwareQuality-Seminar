package example.beanConfiguration;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.function.BooleanSupplier;

@Configuration
public class DefaultBean {
    @Bean
    public BooleanSupplier defaultTruthValue() {
        return () -> true;
    }
}
