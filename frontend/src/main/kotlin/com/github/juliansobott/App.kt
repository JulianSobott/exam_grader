package com.github.juliansobott

import com.github.juliansobott.components.CodeSnippet
import com.github.juliansobott.components.CodeType
import com.github.juliansobott.components.TestCase
import com.github.juliansobott.components.TestCaseStatus
import pl.treksoft.kvision.Application
import pl.treksoft.kvision.html.div
import pl.treksoft.kvision.i18n.DefaultI18nManager
import pl.treksoft.kvision.i18n.I18n
import pl.treksoft.kvision.module
import pl.treksoft.kvision.panel.root
import pl.treksoft.kvision.require
import pl.treksoft.kvision.rest.RestClient
import pl.treksoft.kvision.startApplication
import kotlin.js.Promise

class App : Application() {
    init {
        require("css/kvapp.css")
        require("css/prism-atom-dark.css")
    }

    override fun start() {
        I18n.manager =
            DefaultI18nManager(
                mapOf(
                    "pl" to require("i18n/messages-pl.json"),
                    "en" to require("i18n/messages-en.json")
                )
            )

        root("kvapp") {
            val exampleCode = "public static void main(String[] args) {\n" +
                    " System.out.println(\"Hello, World\");\n" +
                    "}"
            add(
                TaskElement(
                    Task(
                        listOf(
                            SubTask(
                                "A task description", 10,
                                listOf(CodeSnippet(exampleCode, CodeType.METHOD, name = "toString")),
                                listOf(TestCase("test1", TestCaseStatus.PASSED))
                            ),
                            SubTask(
                                "Another subtask", 10,
                                listOf(CodeSnippet(exampleCode, CodeType.METHOD, name = "toStrings")),
                                listOf(TestCase("test2", TestCaseStatus.FAILED, "AssertionError: 10 != 20"))
                            )
                        ),
                        20, 1, 2, 3
                    )
                )
            )
            val restClient = RestClient()
            val result: Promise<String> = restClient.call("http://127.0.0.1:8080")
            result.then { s ->
                div(s)
            }
            result.catch {
                div(it.message)
            }
            // TODO
        }
    }
}

fun main() {
    startApplication(::App, module.hot)
}
