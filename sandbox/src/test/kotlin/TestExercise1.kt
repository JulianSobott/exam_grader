import kotlin.test.assertEquals
import org.junit.jupiter.api.*

class TestExercise1 {

    @Test
    fun `1a) test me`() {
        val a = MyClass1()
        assertEquals(a.getNumber(), 20)
    }

    @Test
    fun `1a) test me fail`() {
        assert(false)
    }
}