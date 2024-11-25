import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, url_for


def load_clubs():
    with open("clubs.json") as c:
        list_of_clubs = json.load(c)["clubs"]
        return list_of_clubs


def load_competitions():
    with open("competitions.json") as comps:
        list_of_competitions = json.load(comps)["competitions"]
        for c in list_of_competitions:
            c["finished"] = (
                datetime.strptime(c["date"], "%Y-%m-%d %H:%M:%S") < datetime.now()
            )
            try:
                c["registered"]
            except KeyError:
                c["registered"] = {}
        return list_of_competitions


def get_places_booked(competition, club_name):
    for key in competition["registered"]:
        if key == club_name:
            return competition["registered"][key]
    return 0


app = Flask(__name__)
app.secret_key = "something_special"

competitions = load_competitions()
clubs = load_clubs()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/show-summary", methods=["POST"])
def showSummary():
    try:
        club = [club for club in clubs if club["email"] == request.form["email"]][0]
    except IndexError:
        flash("Sorry, that email wasn't found.")
        return render_template("index.html"), 401
    return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/book/<competition>/<club>")
def book(competition, club):
    try:
        foundClub = [c for c in clubs if c["name"] == club][0]
        foundCompetition = [c for c in competitions if c["name"] == competition][0]
        if foundCompetition["finished"]:
            flash("Sorry, this competition has already ended.")
            return (
                render_template("welcome.html", club=club, competitions=competitions),
                302,
            )
        if foundClub and foundCompetition:
            return render_template(
                "booking.html", club=foundClub, competition=foundCompetition
            )
        else:
            flash("Not found: this resource does not exists")
            return render_template("welcome.html", club=club, competitions=competitions)
    except IndexError:
        flash("Something went wrong-please try again")
        return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/purchase-places", methods=["POST"])
def purchasePlaces():
    competition = [c for c in competitions if c["name"] == request.form["competition"]][
        0
    ]
    club = [c for c in clubs if c["name"] == request.form["club"]][0]
    placesRequired = int(request.form["places"])
    places_booked = int(get_places_booked(competition, club["name"]))

    # TODO: Remove for production
    # Bypass validation for locust's performance test
    if app.debug and competition["name"] == "Black Hole":  # pragma: no cover
        competition["numberOfPlaces"] = (
            int(competition["numberOfPlaces"]) - placesRequired
        )
        competition["registered"][club["name"]] = placesRequired + places_booked
        club["points"] = int(club["points"]) - placesRequired
        flash("Great-booking complete!")
        return render_template("welcome.html", club=club, competitions=competitions)

    if competition["finished"]:
        flash("Sorry, this competition has already ended.")
        return (
            render_template("welcome.html", club=club, competitions=competitions),
            410,
        )

    if placesRequired > int(club["points"]):
        flash(f"You do not have enough points. Your points: {club['points']}")
        return render_template("booking.html", club=club, competition=competition), 409

    if placesRequired > 12 or (placesRequired + places_booked) > 12:
        flash("You cannot purchase more than 12 places for the same competition.")
        return render_template("booking.html", club=club, competition=competition), 409

    if int(competition["numberOfPlaces"]) - placesRequired < 0:
        flash(
            f"There is not enough places left: {competition['numberOfPlaces']} remaining places."
        )
        return render_template("booking.html", club=club, competition=competition), 409

    competition["numberOfPlaces"] = int(competition["numberOfPlaces"]) - placesRequired
    competition["registered"][club["name"]] = placesRequired + places_booked
    club["points"] = int(club["points"]) - placesRequired
    flash("Great-booking complete!")
    return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/points-board")
def display_board():
    return render_template("display_board.html", clubs=clubs)


@app.route("/logout")
def logout():
    return redirect(url_for("index"))
