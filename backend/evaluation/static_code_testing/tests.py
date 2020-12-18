import unittest

from static_code_testing.attributes import *
from static_code_testing.class_declaration import *
from static_code_testing.method import *


class TestMethod(unittest.TestCase):

    def test_valid(self):
        failures = test_method(MethodTest("getName", [AccessModifier.PUBLIC], "void", ["String", "Car"]),
                               "public void getName(String args, Car c)")
        self.assertEqual([], failures)

    def test_valid_params_unordered(self):
        failures = test_method(MethodTest("getName", [AccessModifier.PUBLIC], "void", ["String", "Car"], False),
                               "public void getName( Car c, String args)")
        self.assertEqual([], failures)

    def test_access(self):
        failures = test_method(MethodTest("getName", [AccessModifier.PUBLIC], "void", ["String", "Car"]),
                               "void getName(String args, Car c)")
        self.assertEqual([MethodFailure.ACCESS_MODIFIER], failures)

    def test_return(self):
        failures = test_method(MethodTest("getName", [AccessModifier.PUBLIC], "void", ["String", "Car"]),
                               "public String getName(String args, Car c)")
        self.assertEqual([MethodFailure.RETURN_TYPE], failures)

    def test_name(self):
        failures = test_method(MethodTest("getName", [AccessModifier.PUBLIC], "void", ["String", "Car"]),
                               "public void getname(String args, Car c)")
        self.assertEqual([MethodFailure.NAME], failures)

    def test_abstract(self):
        failures = test_method(MethodTest("getName", [AccessModifier.PUBLIC], "void", ["String", "Car"]),
                               "public abstract void getName(String args, Car c)")
        self.assertEqual([MethodFailure.ABSTRACT], failures)

    def test_params(self):
        failures = test_method(MethodTest("getName", [AccessModifier.PUBLIC], "void", ["String", "Car"]),
                               "public void getName(String args)")
        self.assertEqual([MethodFailure.PARAMETERS], failures)

    def test_params_ordered(self):
        failures = test_method(MethodTest("getName", [AccessModifier.PUBLIC], "void", ["String", "Car"]),
                               "public void getName( Car c, String args)")
        self.assertEqual([MethodFailure.PARAMETERS], failures)


class TestClass(unittest.TestCase):

    def test_valid(self):
        failures = test_class(
            ClassTest("Car", "Vehicle", ["You", "Me"], False, [AccessModifier.PUBLIC], ClassType.CLASS),
            "public class Car extends Vehicle implements You, Me"
        )
        self.assertEqual([], failures)

    def test_implements(self):
        failures = test_class(
            ClassTest("Car", "Vehicle", ["You", "Me"], False, [AccessModifier.PUBLIC], ClassType.CLASS),
            "public class Car extends Vehicle implements You"
        )
        self.assertEqual([ClassFailure.IMPLEMENTS], failures)

    def test_extends(self):
        failures = test_class(
            ClassTest("Car", "Vehicle", ["You", "Me"], False, [AccessModifier.PUBLIC], ClassType.CLASS),
            "public class Car implements You, Me"
        )
        self.assertEqual([ClassFailure.EXTENDS], failures)

    def test_type(self):
        failures = test_class(
            ClassTest("Car", "Vehicle", ["You", "Me"], False, [AccessModifier.PUBLIC], ClassType.CLASS),
            "public interface Car extends Vehicle implements You, Me"
        )
        self.assertEqual([ClassFailure.TYPE], failures)

    def test_abstract(self):
        failures = test_class(
            ClassTest("Car", "Vehicle", ["You", "Me"], False, [AccessModifier.PUBLIC], ClassType.CLASS),
            "public abstract class Car extends Vehicle implements You, Me"
        )
        self.assertEqual([ClassFailure.ABSTRACT], failures)


class TestAttribute(unittest.TestCase):

    def test_valid(self):
        failures = test_attribute(
            AttributeTest("color", "String", [AccessModifier.PRIVATE]),
            "private String color;"
        )
        self.assertEqual([], failures)

    def test_name(self):
        failures = test_attribute(
            AttributeTest("color", "String", [AccessModifier.PRIVATE]),
            "private String colors;"
        )
        self.assertEqual([AttributeFailure.NAME], failures)

    def test_access_modifier(self):
        failures = test_attribute(
            AttributeTest("color", "String", [AccessModifier.PRIVATE]),
            "public String color;"
        )
        self.assertEqual([AttributeFailure.ACCESS_MODIFIER], failures)

    def test_static(self):
        failures = test_attribute(
            AttributeTest("color", "String", [AccessModifier.PRIVATE]),
            "private static String color;"
        )
        self.assertEqual([AttributeFailure.STATIC], failures)
