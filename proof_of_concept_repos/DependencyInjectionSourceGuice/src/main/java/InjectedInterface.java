import com.google.inject.ImplementedBy;

@ImplementedBy(CorrectImplementation.class)
public interface InjectedInterface {
    boolean getTrue();

}
