from flask_restx import Namespace, Resource, fields
from difflib import get_close_matches

def GetTodaysSkaters():
    #TODO: get list of skaters from list of skaters going to play today
    #This is a list of skaters paying today october 25th 2023 ( WSH v NJD)
    #testing Google ML Kit detecting Nicklas Backstom as Nicklas Backstronm.
    #Some arbitrary 'N' got added between 'O' and 'M'
    return ['Luke Hughes', 'Lucas Johansen', 'Dawson Mercer', 'T.J. Oshie', 'Curtis Lazar', 'Alexander Holtz', 'Hardy Haman Aktell', 'Jack Hughes', 'John Marino', 'Aliaksei Protas', 'Martin Fehervary', 'Trevor van Riemsdyk', 'Matthew Phillips', 'Nick Jensen', 'Tyler Toffoli', 'Chris Tierney', 'Nico Hischier', 'Nic Dowd', 'Rasmus Sandin', 'Sonny Milano', 'Brendan Smith', 'Evgeny Kuznetsov', 'Alexander Alexeyev', 'Timo Meier', 'Dougie Hamilton', 'Anthony Mantha', 'Beck Malenstyn', 'Dylan Strome', 'Connor McMichael', 'Jesper Bratt', 'John Carlson', 'Alex Ovechkin', 'Tom Wilson', 'Nathan Bastian', 'Erik Haula', 'Kevin Bahl', 'Nicklas Backstrom', 'Tomas Nosek', 'Michael McLeod', 'Ondrej Palat', 'Jonas Siegenthaler']

def SuggestSkater( suggestFromName ):
    #TODO: prevent abuse.  difflib is notoriously computationally intensive
    #   and could be leveraged to DoS from a single system.
    skaters = GetTodaysSkaters()
    ret = {}
    for misspelledName in suggestFromName:
        ret[ misspelledName ] = get_close_matches( misspelledName, skaters, 1)
    return ret

#TODO add to skaters namespace as /skaters/suggest
api = Namespace( "suggest" )

name_parser = api.parser()
name_parser.add_argument('name', type=str, action='split')

@api.route("/")
@api.doc(params={"name": "Skater name that doesn't seem to have a match with existing data."})
class Suggest( Resource ):
    def get( self ):
        args = name_parser.parse_args()
        return SuggestSkater( args[ 'name' ] )