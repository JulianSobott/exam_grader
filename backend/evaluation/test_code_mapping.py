METHOD = 0
ATTRIBUTES = 1
CLASS = 2
CONSTRUCTOR = 3


required_files = ["Mitglied.java", "Leiter.java", "Trainer.java"]

test_suites_order = ["Mitglied", "Trainer", "Leiter"]
test_suite_order_map = {k: i for i, k in enumerate(test_suites_order)}

test_code_mapping = {
    "1 a) attribute": [("Mitglied", ATTRIBUTES)],
    "1 b) Constructors": [("Mitglied", CONSTRUCTOR)],
    "1 c) getters": [("Mitglied", METHOD, "getVorname"), ("Mitglied", METHOD, "getNachname")],
    "1 d) umziehen": [("Mitglied", METHOD, "umziehen")],
    "1 e) toString": [("Mitglied", METHOD, "toString")],
    "1 f) equals": [("Mitglied", METHOD, "equals")],

    "2 a) constructor and extends": [("Trainer", CLASS), ("Trainer", CONSTRUCTOR)],
    "2 b) attributes": [("Trainer", ATTRIBUTES)],
    "2 c) beitragSetzen()": [("Trainer", METHOD, "beitragSetzen")],
    "2 d) stundenAktualisieren()": [("Trainer", METHOD, "stundenAktualisieren")],
    "2 e) toString()": [("Trainer", METHOD, "toString")],

    "3 a) extends + attribute": [("Leiter", CLASS), ("Leiter", ATTRIBUTES), ("Leiter", CONSTRUCTOR)],
    "3 b) kategorieSetzen valid": [("Leiter", METHOD, "kategorieSetzen")],
    "3 b) kategorieSetzen invalid constructor": [("Leiter", CONSTRUCTOR)],
    "3 b) kategorieSetzen invalid fun": [("Leiter", METHOD, "kategorieSetzen")],
    "3 c) beitragSetzen()": [("Leiter", METHOD, "beitragSetzen")],
}

test_points_mapping = {
    "1 a) attribute": 4,
    "1 b) Constructors": 6,
    "1 c) getters": 2,
    "1 d) umziehen": 2,
    "1 e) toString": 3,
    "1 f) equals": 4,

    "2 a) constructor and extends": 5,
    "2 b) attributes": 2,
    "2 c) beitragSetzen()": 4,
    "2 d) stundenAktualisieren()": 3,
    "2 e) toString()": 3,

    "3 a) extends + attribute": 2,
    "3 b) kategorieSetzen valid": 2,    # b) 7 points
    "3 b) kategorieSetzen invalid constructor": 2,
    "3 b) kategorieSetzen invalid fun": 3,
    "3 c) beitragSetzen()": 3,
}
