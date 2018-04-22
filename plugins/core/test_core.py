from unittest import TestCase
from core import Core
from os import path
from datetime import date

fixtures = path.join(path.dirname(__file__), "test_fixtures")


class TestCore(TestCase):
    def test_weekday(self):
        "On a regular weekday we expect a normal menu"
        weekday = date(2018, 4, 20)
        expected = """*MH-kafeen* (stenger *16:00* i dag) serverer:
>*Lunsj*
>• *35,-* Dagens suppe med focaccia
>• *41,-* Risgrøt med saft
>• *52,-* MHs go' blanding
>• *55,-* Rømmegrøt med saft
>*Middag*
>• *74,-* Nachosform med stæsj
*Teorifagskafeen* (stenger *17:00* i dag) serverer:
>*Ukategorisert*
>• *41,-* Fredagsgrøt (Risengrynsgrøt med sukker, kanel, smør og saft.)
>• *43,-* Dagens suppe (Dagens hjemmelagede gluten og laktosefrie suppe)
>*Middag*
>• Garasjesalg
"""

        weekday_menu = Core(
            source=open(path.join(fixtures, "weekday.html")),
            date=weekday
        )

        self.assertEqual(expected, weekday_menu.response())

    def test_weekend(self):
        "On the weekends everything is closed, expect an empty response"
        weekend = date(2018, 4, 21)

        expected = ""

        weekend_menu = Core(
            source=open(path.join(fixtures, "weekend.html")),
            date=weekend
        )

        self.assertEqual(expected, weekend_menu.response())

    def test_triggers(self):
        "Ensure that plugin responds to the correct keywords"
        self.assertTrue(Core.can_respond_to("lunsj pls"))
        self.assertTrue(Core.can_respond_to("I want some lunch"))
        self.assertTrue(Core.can_respond_to("hva er til middag?"))
        self.assertTrue(Core.can_respond_to("din din dinner me up"))
