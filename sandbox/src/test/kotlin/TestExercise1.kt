import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class TestExercise1 {

    @Test
    fun `1a) test me`() {
        val a = MyClass1()
        assertEquals(a.getNumber(), 20)
    }

    @Test
    fun `1a) test me fail`() {
        assertTrue(false)
    }

    @Test
    fun `1b) another`() {
        assertTrue(true)
    }
}