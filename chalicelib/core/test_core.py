from unittest import TestCase
from unittest.mock import patch
from core import Core
from os import path
from datetime import date

fixtures = path.join(path.dirname(__file__), "test_fixtures")


class TestCore(TestCase):
    def test_weekday(self):
        "On a regular weekday we expect a normal menu"
        weekday = date(2018, 4, 20)
        expected = """*MH-kafeen* (closes at *16:00* today) are serving:
>*Lunsj*
>• *35,-* Dagens suppe med focaccia
>• *41,-* Risgrøt med saft
>• *52,-* MHs go' blanding
>• *55,-* Rømmegrøt med saft
>*Middag*
>• *74,-* Nachosform med stæsj
*Teorifagskafeen* (closes at *17:00* today) are serving:
>*Hele dagen*
>• *41,-* Fredagsgrøt (Risengrynsgrøt med sukker, kanel, smør og saft.)
>• *43,-* Dagens suppe (Dagens hjemmelagede gluten og laktosefrie suppe)
>*Middag*
>• Garasjesalg
"""

        weekday_menu = Core(
            source=open(path.join(fixtures, "weekday.html")), date=weekday
        )
        self.maxDiff = None
        self.assertEqual(expected, weekday_menu.response())

    def test_weekend(self):
        "On the weekends everything is closed, expect an empty response"
        weekend = date(2018, 4, 21)

        expected = "The cafeterias are closed today."

        weekend_menu = Core(
            source=open(path.join(fixtures, "weekend.html")), date=weekend
        )

        self.assertEqual(expected, weekend_menu.response())

    def test_triggers(self):
        "Ensure that plugin responds to the correct keywords"
        with patch("core.date") as weekday_date:
            weekday_date.today = Weekday
            self.assertTrue(Core.can_respond_to("lunsj pls"))
            self.assertTrue(Core.can_respond_to("I want some lunch"))
            self.assertTrue(Core.can_respond_to("hva er til middag?"))
            self.assertTrue(Core.can_respond_to("din din dinner me up"))


class Weekday:
    def weekday(self):
        return True
