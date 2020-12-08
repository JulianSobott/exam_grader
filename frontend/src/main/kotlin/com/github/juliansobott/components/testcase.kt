package com.github.juliansobott.components

import pl.treksoft.kvision.core.Background
import pl.treksoft.kvision.core.Col
import pl.treksoft.kvision.core.Color
import pl.treksoft.kvision.core.Style
import pl.treksoft.kvision.html.Span
import pl.treksoft.kvision.panel.SimplePanel
import pl.treksoft.kvision.tabulator.ColumnDefinition
import pl.treksoft.kvision.tabulator.Layout
import pl.treksoft.kvision.tabulator.TabulatorOptions
import pl.treksoft.kvision.tabulator.tabulator

enum class TestCaseStatus(val cssClass: String, val repr: String) {
    FAILED("failed", "FAILED"),
    PASSED("passed", "PASSED"),
    NOT_TESTED("not_tested", "NOT TESTED")
}

data class TestCase(val name: String, val status: TestCaseStatus, val errorMsg: String? = null)

class TestCaseElement(testCases: List<TestCase>) : SimplePanel() {
    init {
        fun statusStyle(className: String, color: Color): Style {
            return Style(className) {
                background = Background(color)
            }
        }

        val styles = mapOf(
            TestCaseStatus.PASSED to statusStyle("passed", Color.name(Col.GREEN)),
            TestCaseStatus.FAILED to statusStyle("failed", Color.name(Col.RED)),
            TestCaseStatus.NOT_TESTED to statusStyle("not_tested", Color.name(Col.YELLOW)),
        )


        tabulator(
            // TODO: color rows not just cells
            testCases,
            options = TabulatorOptions(
                layout = Layout.FITCOLUMNS,
                columns = listOf(
                    ColumnDefinition("Name", formatterComponentFunction = { _, _, data ->
                        Span(data.name) {
                            addCssStyle(styles.getOrElse(data.status, { Style() }))
                        }
                    }),
                    ColumnDefinition("Status", formatterComponentFunction = { _, _, data ->
                        Span(data.status.repr) {
                            addCssStyle(styles.getOrElse(data.status, { Style() }))
                        }
                    }),
                    ColumnDefinition("Error", formatterComponentFunction = { _, _, data ->
                        Span(data.errorMsg) {
                            addCssStyle(styles.getOrElse(data.status, { Style() }))
                        }
                    }),
                )
            ),
        )
    }
}
