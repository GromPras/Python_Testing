import json
from datetime import datetime
from flask import render_template, request, flash, current_app
from app.booking import bp


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


competitions = load_competitions()
clubs = load_clubs()


@bp.route("/show-summary", methods=["POST"])
def show_summary():
    try:
        club = [club for club in clubs if club["email"] == request.form["email"]][0]
    except IndexError:
        flash("Sorry, that email wasn't found.")
        return render_template("index.html"), 401
    return render_template("booking/welcome.html", club=club, competitions=competitions)


@bp.route("/book/<competition>/<club>")
def book(competition, club):
    try:
        found_club = [c for c in clubs if c["name"] == club][0]
        found_competition = [c for c in competitions if c["name"] == competition][0]
        if found_competition["finished"]:
            flash("Sorry, this competition has already ended.")
            return (
                render_template(
                    "booking/welcome.html", club=club, competitions=competitions
                ),
                302,
            )
        if found_club and found_competition:
            return render_template(
                "booking/booking.html", club=found_club, competition=found_competition
            )
        else:
            flash("Not found: this resource does not exists")
            return render_template(
                "booking/welcome.html", club=club, competitions=competitions
            )
    except IndexError:
        flash("Something went wrong-please try again")
        return render_template(
            "booking/welcome.html", club=club, competitions=competitions
        )


@bp.route("/purchase-places", methods=["POST"])
def purchase_places():
    competition = [c for c in competitions if c["name"] == request.form["competition"]][
        0
    ]
    club = [c for c in clubs if c["name"] == request.form["club"]][0]
    places_required = int(request.form["places"])
    places_booked = int(get_places_booked(competition, club["name"]))

    # TODO: Remove for production
    # Bypass validation for locust's performance test
    if current_app.debug and competition["name"] == "Black Hole":  # pragma: no cover
        competition["number_of_places"] = (
            int(competition["number_of_places"]) - places_required
        )
        competition["registered"][club["name"]] = places_required + places_booked
        club["points"] = int(club["points"]) - places_required
        flash("Great-booking complete!")
        return render_template(
            "booking/welcome.html", club=club, competitions=competitions
        )

    if competition["finished"]:
        flash("Sorry, this competition has already ended.")
        return (
            render_template(
                "booking/welcome.html", club=club, competitions=competitions
            ),
            410,
        )

    if places_required > int(club["points"]):
        flash(f"You do not have enough points. Your points: {club['points']}")
        return (
            render_template("booking/booking.html", club=club, competition=competition),
            409,
        )

    if places_required > 12 or (places_required + places_booked) > 12:
        flash("You cannot purchase more than 12 places for the same competition.")
        return (
            render_template("booking/booking.html", club=club, competition=competition),
            409,
        )

    if int(competition["number_of_places"]) - places_required < 0:
        flash(
            f"There is not enough places left: {competition['number_of_places']} remaining places."
        )
        return (
            render_template("booking/booking.html", club=club, competition=competition),
            409,
        )

    competition["number_of_places"] = (
        int(competition["number_of_places"]) - places_required
    )
    competition["registered"][club["name"]] = places_required + places_booked
    club["points"] = int(club["points"]) - places_required
    flash("Great-booking complete!")
    return render_template("booking/welcome.html", club=club, competitions=competitions)


@bp.route("/points-board")
def display_board():
    return render_template("booking/display_board.html", clubs=clubs)
