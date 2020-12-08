package com.github.juliansobott.components

import pl.treksoft.kvision.core.Container
import pl.treksoft.kvision.html.code
import pl.treksoft.kvision.html.customTag
import pl.treksoft.kvision.html.label
import pl.treksoft.kvision.i18n.tr
import pl.treksoft.kvision.panel.SimplePanel

enum class CodeType(val human_readable: String) {
    METHOD(tr("method")),
    CONSTRUCTOR(tr("constructor")),
    ATTRIBUTES(tr("attributes")),
    CLASS_HEADER(tr("class header"))
}

data class CodeSnippet(val code: String, val type: CodeType, val name: String?)

class CodeSnippetElement(code: CodeSnippet) : SimplePanel() {
    init {
        if (code.name != null) {
            label(code.name)
        }
        label(code.type.human_readable)
        customTag("pre") {
            code(code.code, classes = setOf("language-java"))
        }
        // js("Prism.highlightAll();") Maybe something like this is needed when loading async
    }
}

class MultiCodeSnippetsElement(snippets: List<CodeSnippet>) : SimplePanel() {
    init {
        for (snippet in snippets) {
            codeSnippet(snippet)
        }
    }
}


fun Container.codeSnippet(codeSnippet: CodeSnippet): CodeSnippetElement {
    val p = CodeSnippetElement(codeSnippet)
    this.add(p)
    return p
}

fun Container.multiCodeSnippets(snippets: List<CodeSnippet>): MultiCodeSnippetsElement {
    val p = MultiCodeSnippetsElement(snippets)
    this.add(p)
    return p
}