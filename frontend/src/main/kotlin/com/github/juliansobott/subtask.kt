package com.github.juliansobott

import com.github.juliansobott.components.*
import pl.treksoft.kvision.panel.SimplePanel

/*
- comment
- points
- description
- code-snippets
- test cases
 */
data class SubTask(
    val description: String,
    val maxPoints: Number,
    val codeSnippets: List<CodeSnippet>,
    val testCases: List<TestCase>
)

class SubTaskElement(subTask: SubTask) : SimplePanel() {

    val pointsElement = PointsElement(Points(0, subTask.maxPoints))

    init {
        add(pointsElement)
        val commentElement = comment()
        description(subTask.description)
        multiCodeSnippets(subTask.codeSnippets)
        // TODO: relation between test cases and code snippets

        add(TestCaseElement(subTask.testCases))
    }
}