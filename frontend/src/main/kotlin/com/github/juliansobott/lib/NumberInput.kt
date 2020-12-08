package com.github.juliansobott.lib

import com.github.snabbdom.VNode
import org.w3c.dom.HTMLInputElement
import pl.treksoft.kvision.core.Container
import pl.treksoft.kvision.core.StringBoolPair
import pl.treksoft.kvision.core.StringPair
import pl.treksoft.kvision.core.Widget
import pl.treksoft.kvision.form.FormInput
import pl.treksoft.kvision.form.InputSize
import pl.treksoft.kvision.form.ValidationStatus
import pl.treksoft.kvision.state.ObservableState
import pl.treksoft.kvision.state.bind
import pl.treksoft.kvision.utils.set

internal const val DEFAULT_STEP = 1

/**
 * Number input component.
 *
 * @constructor
 * @param value range input value
 * @param min minimal value (default 0)
 * @param max maximal value (default 100)
 * @param step step value (default 1)
 * @param classes a set of CSS class names
 */
open class NumberInput(
        value: Number? = null, min: Number = 0, max: Number = 100, step: Number = DEFAULT_STEP,
        classes: Set<String> = setOf()
) : Widget(classes + "form-control-range"), FormInput, ObservableState<Number?> {

    protected val observers = mutableListOf<(Number?) -> Unit>()

    /**
     * Range input value.
     */
    var value by refreshOnUpdate(value ?: (min as Number?)) { refreshState(); observers.forEach { ob -> ob(it) } }

    /**
     * The value attribute of the generated HTML input element.
     *
     * This value is placed directly in generated HTML code, while the [value] property is dynamically
     * bound to the range input value.
     */
    var startValue by refreshOnUpdate(value) { this.value = it; refresh() }

    /**
     * Minimal value.
     */
    var min by refreshOnUpdate(min)

    /**
     * Maximal value.
     */
    var max by refreshOnUpdate(max)

    /**
     * Step value.
     */
    var step by refreshOnUpdate(step)

    /**
     * The name attribute of the generated HTML input element.
     */
    override var name: String? by refreshOnUpdate()

    /**
     * Determines if the field is disabled.
     */
    override var disabled by refreshOnUpdate(false)

    /**
     * Determines if the range input is automatically focused.
     */
    var autofocus: Boolean? by refreshOnUpdate()

    /**
     * Determines if the range input is read-only.
     */
    var readonly: Boolean? by refreshOnUpdate()

    /**
     * The size of the input.
     */
    override var size: InputSize? by refreshOnUpdate()

    /**
     * The validation status of the input.
     */
    override var validationStatus: ValidationStatus? by refreshOnUpdate()

    init {
        this.setInternalEventListener<NumberInput> {
            input = {
                self.changeValue()
            }
        }
    }

    override fun render(): VNode {
        return render("input")
    }

    override fun getSnClass(): List<StringBoolPair> {
        val cl = super.getSnClass().toMutableList()
        validationStatus?.let {
            cl.add(it.className to true)
        }
        size?.let {
            cl.add(it.className to true)
        }
        return cl
    }

    override fun getSnAttrs(): List<StringPair> {
        val sn = super.getSnAttrs().toMutableList()
        sn.add("type" to "number")
        startValue?.let {
            sn.add("value" to "$it")
        }
        name?.let {
            sn.add("name" to it)
        }
        sn.add("min" to "$min")
        sn.add("max" to "$max")
        sn.add("step" to "$step")
        autofocus?.let {
            if (it) {
                sn.add("autofocus" to "autofocus")
            }
        }
        readonly?.let {
            if (it) {
                sn.add("readonly" to "readonly")
            }
        }
        if (disabled) {
            sn.add("disabled" to "disabled")
        }
        return sn
    }

    override fun afterInsert(node: VNode) {
        refreshState()
    }

    /**
     * Returns the value of the spinner as a String.
     * @return value as a String
     */
    fun getValueAsString(): String? {
        return value?.toString()
    }

    /**
     * Change value in plus.
     */
    open fun stepUp(): NumberInput {
        (getElement() as? HTMLInputElement)?.stepUp()
        return this
    }

    /**
     * Change value in minus.
     */
    open fun stepDown(): NumberInput {
        (getElement() as? HTMLInputElement)?.stepDown()
        return this
    }

    /**
     * @suppress
     * Internal function
     */
    protected open fun refreshState() {
        value?.let {
            getElementJQuery()?.`val`(it)
        }
        if (value == null) value = min
    }

    /**
     * @suppress
     * Internal function
     */
    protected open fun changeValue() {
        val v = getElementJQuery()?.`val`() as String?
        if (v != null && v != "") {
            this.value = v.toDoubleOrNull()
        } else {
            this.value = null
        }
    }

    /**
     * Makes the input element focused.
     */
    override fun focus() {
        getElementJQuery()?.focus()
    }

    /**
     * Makes the input element blur.
     */
    override fun blur() {
        getElementJQuery()?.blur()
    }

    override fun getState(): Number? = value

    override fun subscribe(observer: (Number?) -> Unit): () -> Unit {
        observers += observer
        observer(value)
        return {
            observers -= observer
        }
    }
}

/**
 * DSL builder extension function.
 *
 * It takes the same parameters as the constructor of the built component.
 */
fun Container.numberInput(
        value: Number? = null, min: Number = 0, max: Number = 100, step: Number = DEFAULT_STEP,
        classes: Set<String>? = null,
        className: String? = null,
        init: (NumberInput.() -> Unit)? = null
): NumberInput {
    val rangeInput = NumberInput(value, min, max, step, classes ?: className.set).apply { init?.invoke(this) }
    this.add(rangeInput)
    return rangeInput
}

/**
 * DSL builder extension function for observable state.
 *
 * It takes the same parameters as the constructor of the built component.
 */
fun <S> Container.numberInput(
        state: ObservableState<S>,
        value: Number? = null, min: Number = 0, max: Number = 100, step: Number = DEFAULT_STEP,
        classes: Set<String>? = null,
        className: String? = null,
        init: (NumberInput.(S) -> Unit)
) = numberInput(value, min, max, step, classes, className).bind(state, true, init)
