public class MyClass2 extends MyClass1 {

    private int[] numbers = new int[]{1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

    public int[] getNumbers() {
        return this.numbers;
    }

    public int getN(int i) {
        return this.numbers[i];
    }
}