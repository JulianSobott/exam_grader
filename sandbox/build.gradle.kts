plugins {
    java
    kotlin("jvm") version "1.4.10"
}

group = "com.github"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
}

dependencies {
    implementation(kotlin("stdlib"))
    implementation("org.junit.jupiter:junit-jupiter:5.4.2")
    testImplementation("junit", "junit", "4.12")
}
