import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Assertions.*

class TestExercise2 {

    @Test
    fun `2a) getNumbers`() {
        val a = MyClass2()
        assertEquals(a.getNumbers().size, 10)
    }
}