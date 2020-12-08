package com.github.juliansobott.components

import pl.treksoft.kvision.core.Container
import pl.treksoft.kvision.html.p
import pl.treksoft.kvision.panel.SimplePanel

class DescriptionElement(description: String) : SimplePanel() {
    init {
        p(description)
    }
}

fun Container.description(description: String): DescriptionElement {
    val p = DescriptionElement(description)
    this.add(p)
    return p
}