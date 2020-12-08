package com.github.juliansobott.components

import NumberField
import number
import pl.treksoft.kvision.core.Col
import pl.treksoft.kvision.core.Color
import pl.treksoft.kvision.core.FlexDirection
import pl.treksoft.kvision.core.Style
import pl.treksoft.kvision.html.div
import pl.treksoft.kvision.panel.SimplePanel
import pl.treksoft.kvision.panel.flexPanel
import pl.treksoft.kvision.state.ObservableValue


data class Points(var value: Number, val maxPoints: Number)

class PointsElement(points: Points) : SimplePanel() {

    private val isMax = ObservableValue(false)

    init {

        val actualPointsField = NumberField(points.value, min = 0, max = points.maxPoints, step = 0.5)

        flexPanel(FlexDirection.ROW) {
            add(actualPointsField)
            number(points.maxPoints) {
                readonly = true
            }
        }

        actualPointsField.subscribe { number ->
            if (number != null) {
                points.value = number
                isMax.value = points.value == points.maxPoints
            }
        }

        // handle max value
        val passedStyle = Style {
            color = Color.name(Col.GREEN)
        }
        val notPassedStyle = Style {
            color = Color.name(Col.RED)
        }
        isMax.subscribe {
            if (it) {
                addCssStyle(passedStyle)
                removeCssStyle(notPassedStyle)
            } else {
                addCssStyle(notPassedStyle)
                removeCssStyle(passedStyle)
            }
        }
        // Initial values
        actualPointsField.setValue(points.value)
    }

}

class PointsMerge(val maxPoints: Number) : ObservableValue<Number>(0) {
    private val pointsElements = ArrayList<PointsElement>()

    init {
        addElements(pointsElements)
    }

    fun addElements(newElements: List<PointsElement>) {
//        for (pointElement in newElements) {
//            pointElement.points.subscribe {
//                update()
//            }
//            pointsElements.add(pointElement)
//        }
//        this.update()
    }

    private fun update() {
//        this.value = pointsElements.sumByDouble { it.points.value.toDouble() }
    }
}

class PointsMergeElement(val pointsMerge: PointsMerge) : SimplePanel() {
    init {
        div(pointsMerge) { state ->
            +"$state/${pointsMerge.maxPoints}"
        }
    }
}
