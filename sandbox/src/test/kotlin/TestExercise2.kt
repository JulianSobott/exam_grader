import kotlin.test.assertEquals
import org.junit.jupiter.api.*

class TestExercise2 {

    @Test
    fun `2a) getNumbers`() {
        val a = MyClass2()
        assertEquals(a.getNumbers().length, 10)
    }
}