package com.github.juliansobott.components

import pl.treksoft.kvision.core.Container
import pl.treksoft.kvision.form.text.TextArea
import pl.treksoft.kvision.panel.SimplePanel
import pl.treksoft.kvision.state.ObservableValue

class Comment(value: String = "") : ObservableValue<String>(value)

class CommentElement() : SimplePanel() {

    val comment: Comment = Comment()

    init {
        add(TextArea(value = comment.value))
    }
}


fun Container.comment(): CommentElement {
    val p = CommentElement()
    this.add(p)
    return p
}