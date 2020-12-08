package com.github.juliansobott

import com.github.juliansobott.components.PointsElement
import com.github.juliansobott.components.PointsMerge
import com.github.juliansobott.components.PointsMergeElement
import pl.treksoft.kvision.panel.SimplePanel

data class Task(
    val subTasks: List<SubTask>,
    val maxPoints: Number,
    val numPassed: Int,
    val numFailed: Int,
    val numNotTested: Int
)

class TaskElement(task: Task) : SimplePanel() {
    init {
        // TODO: num...

        val subTaskElements = ArrayList<SubTaskElement>()
        val pointElements = ArrayList<PointsElement>()
        for (subTask in task.subTasks) {
            val element = SubTaskElement(subTask)
            subTaskElements.add(element)
            pointElements.add(element.pointsElement)
        }
        val pointsMergeElement = PointsMergeElement(PointsMerge(task.maxPoints))
        pointsMergeElement.pointsMerge.addElements(pointElements)

        add(pointsMergeElement)
        for (subTaskElement in subTaskElements) {
            add(subTaskElement)
        }
    }
}