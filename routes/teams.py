@api.route('/<int:year>/<team>')
def team( year, team ):
    return "Teams"