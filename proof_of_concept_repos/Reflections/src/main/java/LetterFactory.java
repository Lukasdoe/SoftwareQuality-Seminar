public class LetterFactory {
    public static Letter createLetterInstance(char letter) {
        try {
            Class<?> letterClass =
                    Class.forName("Letter" + letter);
            return (Letter) letterClass.newInstance();
        } catch (ClassNotFoundException | InstantiationException | IllegalAccessException e) {
            e.printStackTrace();
            return null;
        }
    }
}
