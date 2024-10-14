import json
from flask import render_template, request, flash
from app.booking import bp


def loadClubs():
    with open("clubs.json") as c:
        listOfClubs = json.load(c)["clubs"]
        return listOfClubs


def loadCompetitions():
    with open("competitions.json") as comps:
        listOfCompetitions = json.load(comps)["competitions"]
        for c in listOfCompetitions:
            c["subscriptions"] = {}
        return listOfCompetitions


def getPlacesBooked(competition, clubName):
    for key in competition["subscriptions"]:
        if key == clubName:
            return competition["subscriptions"][key]
    return 0


competitions = loadCompetitions()
clubs = loadClubs()


@bp.route("/showSummary", methods=["POST"])
def showSummary():
    try:
        club = [club for club in clubs if club["email"] == request.form["email"]][
            0
        ] or None
    except IndexError:
        flash("Sorry, that email was not found.")
        return render_template("index.html")
    return render_template("booking/welcome.html", club=club, competitions=competitions)


@bp.route("/book/<competition>/<club>")
def book(competition, club):
    foundClub = [c for c in clubs if c["name"] == club][0]
    foundCompetition = [c for c in competitions if c["name"] == competition][0]
    if foundClub and foundCompetition:
        return render_template(
            "booking/booking.html", club=foundClub, competition=foundCompetition
        )
    else:
        flash("Something went wrong-please try again")
        return render_template(
            "booking/welcome.html", club=club, competitions=competitions
        )


@bp.route("/purchasePlaces", methods=["POST"])
def purchasePlaces():
    competition = [c for c in competitions if c["name"] == request.form["competition"]][
        0
    ]
    club = [c for c in clubs if c["name"] == request.form["club"]][0]
    placesRequired = int(request.form["places"])
    placesBooked = int(getPlacesBooked(competition, club["name"]))
    if placesRequired > int(club["points"]):
        flash(f"You do not have enough points. Your points: {club['points']}")
        return render_template(
            "booking/booking.html", club=club, competition=competition
        )
    if placesRequired > 12 or (placesRequired + placesBooked) > 12:
        flash("Sorry, you can only book up to 12 places.")
        return render_template(
            "booking/booking.html", club=club, competition=competition
        )
    else:
        competition["numberOfPlaces"] = (
            int(competition["numberOfPlaces"]) - placesRequired
        )
        competition["subscriptions"][club["name"]] = placesRequired
        flash("Great-booking complete!")
        return render_template(
            "booking/welcome.html", club=club, competitions=competitions
        )
