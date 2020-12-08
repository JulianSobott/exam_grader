package com.github.juliansobott

import kotlinx.serialization.Serializable
import pl.treksoft.kvision.rest.RestClient
import kotlin.js.Promise


// submission, task, subtask, category(points, comment)     // TODO: typesafe
data class Identifier(val identifiers: List<String>) {
    fun toUri(): String {
        return identifiers.joinToString("/")
    }
}

abstract class ApiElement<T>(initialValue: T, private val identifier: Identifier) {

    fun save() {
        val restClient = RestClient()
        val uri = identifier.toUri()
        val res: Promise<dynamic> = restClient.remoteCall("http://localhost:8080/$uri", getData())
        // TODO: handle res
    }

    abstract fun getData(): Serializable
}