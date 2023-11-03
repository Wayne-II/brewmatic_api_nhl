from flask_restx import Namespace, Resource, fields
from difflib import get_close_matches

def GetTodaysSkaters():
    #TODO: get list of skaters from list of skaters going to play today
    #This is a list of skaters paying today october 25th 2023 ( WSH v NJD)
    #testing Google ML Kit detecting Nicklas Backstom as Nicklas Backstronm.
    #Some arbitrary 'N' got added between 'O' and 'M'
    # return ['Mike Matheson', 'Alex Iagallo', 'Luke Hughes', 'Lucas Johansen', 'Dawson Mercer', 'T.J. Oshie', 'Curtis Lazar', 'Alexander Holtz', 'Hardy Haman Aktell', 'Jack Hughes', 'John Marino', 'Aliaksei Protas', 'Martin Fehervary', 'Trevor van Riemsdyk', 'Matthew Phillips', 'Nick Jensen', 'Tyler Toffoli', 'Chris Tierney', 'Nico Hischier', 'Nic Dowd', 'Rasmus Sandin', 'Sonny Milano', 'Brendan Smith', 'Evgeny Kuznetsov', 'Alexander Alexeyev', 'Timo Meier', 'Dougie Hamilton', 'Anthony Mantha', 'Beck Malenstyn', 'Dylan Strome', 'Connor McMichael', 'Jesper Bratt', 'John Carlson', 'Alex Ovechkin', 'Tom Wilson', 'Nathan Bastian', 'Erik Haula', 'Kevin Bahl', 'Nicklas Backstrom', 'Tomas Nosek', 'Michael McLeod', 'Ondrej Palat', 'Jonas Siegenthaler']

    return ["Travis Konecny", "Filip Chytil", "Brock Nelson", "Barclay Goodrow", "Milan Lucic", "Chad Ruhwedel", "Rickard Rakell", "Jimmy Vesey", "Mathew Barzal", "Braden Schneider", "Jacob Trouba", "Sean Couturier", "Tyler Pitlick", "Kevin Shattenkirk", "Sidney Crosby", "Ryan Graves", "Owen Tippett", "Scott Mayfield", "Jean-Gabriel Pageau", "Drew O'Connor", "Kaapo Kakko", "Hudson Fasching", "Noah Dobson", "Nicolas Deslauriers", "Sebastian Aho", "Egor Zamula", "Radim Zohorna", "Lars Eller", "Blake Wheeler", "Will Cuylle", "K'Andre Miller", "Bo Horvat", "Casey Cizikas", "Travis Sanheim", "Cal Clutterbuck", "Tyson Foerster", "Chris Kreider", "Mika Zibanejad", "Morgan Frost", "Joel Farabee", "Adam Fox", "Matt Nieto", "Samuel Bolduc", "Cam Atkinson", "Marcus Pettersson", "Bryan Rust", "Ryan Pulock", "Jake Guentzel", "Kyle Palmieri", "Bobby Brink", "Garnet Hathaway", "Alexis Lafreniere", "Charlie Coyle", "Matt Martin", "Ryan Lindgren", "Julien Gauthier", "Pierre Engvall", "Oliver Wahlstrom", "Marc Staal", "Erik Gustafsson", "Nick Bonino", "Vincent Trocheck", "Alexander Romanov", "Scott Laughton", "Erik Karlsson", "Jeff Carter", "Zac Jones", "Pierre-Olivier Joseph", "Evgeni Malkin", "Ryan Shea", "Ryan Poehling", "Noel Acciari", "Adam Pelech", "John Ludvig", "Reilly Smith", "Sean Walker", "Brad Marchand", "Kris Letang", "James van Riemsdyk", "Anders Lee", "Simon Holmstrom", "Noah Cates", "Nick Seeler", "Cam York", "Artemi Panarin", "Brendan Gallagher", "Jake McCabe", "Calle Jarnkrok", "Jesse Ylonen", "John Beecher", "Kirby Dach", "Pontus Holmberg", "Parker Kelly", "Fraser Minten", "Jordan Martinook", "Sean Monahan", "Alex Newhook", "William Nylander", "Matt Grzelcyk", "Rafael Harvey-Pinard", "Mark Giordano", "John Klingberg", "Hampus Lindholm", "Jake Evans", "Vladimir Tarasenko", "Tim Stutzle", "Kaiden Guhle", "Matthew Poitras", "Brent Burns", "Juraj Slafkovsky", "Jordan Staal", "Jake DeBrusk", "Max Domi", "Ryan Reaves", "Jakob Chychrun", "Morgan Rielly", "Teuvo Teravainen", "Jacob Bernard-Docker", "Brady Skjei", "Drake Batherson", "Auston Matthews", "Timothy Liljegren", "Michael Pezzetta", "Trent Frederic", "Mitchell Marner", "Jaccob Slavin", "Mark Kastelic", "Rourke Chartier", "Cole Caufield", "Tanner Pearson", "Mike Matheson", "Jakub Lauko", "Johnathan Kovacevic", "Matthew Knies", "Dmitry Orlov", "Thomas Chabot", "David Kampf", "Morgan Geekie", "Artem Zub", "Jake Sanderson", "Josh Anderson", "Brandon Carlo", "David Savard", "Stefan Noesen", "Arber Xhekaj", "Gustav Lindstrom", "Noah Gregor", "Charlie McAvoy", "Patrick Brown", "David Pastrnak", "Tony DeAngelo", "John Tavares", "Pavel Zacha", "Josh Norris", "TJ Brodie", "Dominik Kubalik", "Travis Hamonic", "Erik Brannstrom", "Mathieu Joseph", "Derek Forbort", "Ridly Greig", "Tyler Bertuzzi", "Nick Suzuki", "Brady Tkachuk", "Jordan Harris", "Brett Pesce", "Jesper Fast", "Justin Barron", "Claude Giroux", "Jordan Kyrou", "Blake Coleman", "Nick Perbix", "Christian Fischer", "Michael Eyssimont", "Nick Leddy", "Robert Thomas", "Brayden Point", "Michael Bunting", "Oskar Sundqvist", "Victor Hedman", "Ben Chiarot", "Jonatan Berggren", "Klim Kostin", "Marco Scandella", "Jake Neighbours", "Justin Faulk", "Kevin Hayes", "Waltteri Merela", "Sammy Blais", "Jakub Vrana", "J.T. Compher", "Zach Bogosian", "Jack Drury", "Jesperi Kotkaniemi", "Jalen Chatfield", "Joe Veleno", "Colton Parayko", "Anthony Cirelli", "Dennis Gilbert", "Jordan Oesterle", "Alex DeBrincat", "Martin Necas", "Calvin de Haan", "A.J. Greer", "Brendan Lemieux", "Andrew Copp", "Elias Lindholm", "David Perron", "Chris Tanev", "Steven Stamkos", "Erik Cernak", "Andrew Mangiapane", "Nikita Zadorov", "Brandon Saad", "Kasperi Kapanen", "Justin Holl", "Tyler Motte", "Mikhail Sergachev", "Jake Walman", "Tyler Tucker", "Brayden Schenn", "Robby Fabbri", "Dryden Hunt", "Darren Raddysh", "Luke Glendening", "Lucas Raymond", "Moritz Seider", "Daniel Sprong", "Dylan Larkin", "Torey Krug", "Rasmus Andersson", "Jonathan Huberdeau", "Olli Maatta", "Seth Jarvis", "Mikael Backlund", "Brandon Hagel", "Conor Sheary", "Pavel Buchnevich", "Haydn Fleury", "Alexey Toropchenko", "Shayne Gostisbehere", "Nazem Kadri", "Alex Barre-Boulet", "Tanner Jeannot", "Michael Rasmussen", "Nikita Alexandrov", "Nicholas Paul", "Sebastian Aho", "Austin Czarnik", "Austin Watson", "Nikita Kucherov", "Noah Hanifin", "Jeff Petry", "MacKenzie Weegar", "Cale Makar", "Jordan Eberle", "Miles Wood", "Ryan Nugent-Hopkins", "Justin Schultz", "Dylan Holloway", "Devin Shore", "Logan Stanley", "Darnell Nurse", "Mikko Rantanen", "Vince Dunn", "Brett Kulak", "Derek Ryan", "Dillon Dube", "Eeli Tolvanen", "Dylan DeMelo", "Alex Iafallo", "Ross Colton", "Mattias Ekholm", "Jamie Drysdale", "Zach Hyman", "Logan O'Connor", "Mattias Janmark", "Andrew Cogliano", "Yanni Gourde", "Mason Appleton", "Connor McDavid", "Devon Toews", "Neal Pionk", "Will Borgen", "Cody Ceci", "Tomas Tatar", "Kurtis MacDermid", "Ryan Johansen", "Brenden Dillon", "Mark Scheifele", "Samuel Girard", "Morgan Barron", "Andre Burakovsky", "Josh Manson", "Nino Niederreiter", "Vladislav Namestnikov", "Fredrik Olofsson", "Brian Dumoulin", "Ryan McLeod", "Cole Perfetti", "Jared McCann", "Gabriel Vilardi", "Jaden Schwartz", "Pierre-Edouard Bellemare", "Valeri Nichushkin", "Vincent Desharnais", "Warren Foegele", "Alex Wennberg", "Dylan Samberg", "David Gustafsson", "Matty Beniers", "Adam Ruzicka", "Kailer Yamamoto", "Philip Broberg", "Walker Duehr", "Adam Larsson", "Tye Kartye", "Rasmus Kupari", "Bowen Byram", "Matt Coronato", "Oliver Bjorkstrand", "Nikolaj Ehlers", "Yegor Sharangovich", "Adam Henrique", "Leon Draisaitl", "Evander Kane", "Adam Erne", "Kyle Connor", "Evan Bouchard", "Adam Lowry", "Josh Morrissey", "Connor Brown", "Artturi Lehkonen", "Jonathan Drouin", "Jack Johnson", "Jamie Oleksiak", "Brandon Tanev", "Nate Schmidt", "Nathan MacKinnon", "William Eklund", "Ross Johnston", "Erik Gudbranson", "Boone Jenner", "Adam Fantilli", "Mathieu Olivier", "Jan Rutta", "Wyatt Johnston", "Mario Ferraro", "Tyler Seguin", "Luke Kunin", "Mikael Granlund", "Emil Bemstrom", "Fabian Zetterlund", "Sam Steel", "Trevor Zegras", "Cam Fowler", "Kent Johnson", "Mason Marchment", "Andrew Peeke", "Miro Heiskanen", "Pavel Mintyukov", "Alex Goligoski", "David Jiricek", "Esa Lindell", "Thomas Bordeleau", "Ty Emberson", "Max Jones", "Mason McTavish", "Troy Terry", "Jamie Benn", "Cole Sillinger", "Joe Pavelski", "Ryan Suter", "Damon Severson", "Marcus Foligno", "Marc-Edouard Vlasic", "Jake Bean", "Kevin Labanc", "Kirill Marchenko", "Ivan Provorov", "Matt Benning", "Nico Sturm", "Tristan Luneau", "Filip Zadina", "Anthony Duclair", "Sam Carrick", "Johnny Gaudreau", "Brett Leason", "Pat Maroon", "Zach Werenski", "Craig Smith", "Justin Danforth", "Leo Carlsson", "Adam Boqvist", "Givani Smith", "Nikolai Knyzhov", "Alexander Barabanov", "Radek Faksa", "Frank Vatrano", "Ilya Lyubushkin", "Jack Roslovic", "Radko Gudas", "Kyle Burroughs", "Tomas Hertl", "Mike Hoffman", "Bo Groulx", "Jacob Peterson", "Thomas Harley", "Marcus Johansson", "Matt Duchene", "Jakob Silfverberg", "Ryan Strome", "Evgenii Dadonov", "Urho Vaakanainen", "Roope Hintz", "Alexandre Texier", "Nils Lundkvist", "Sean Kuraly", "Jani Hakanpaa", "Jason Robertson", "Patrik Laine", "Ty Dellandrea", "Jackson LaCombe", "Vinni Lettieri", "Frederick Gaudreau", "Kirill Kaprizov", "Mats Zuccarello", "Calen Addison", "Jonas Brodin", "Connor Dewar", "Dakota Mermis", "Matt Boldy", "Ryan Hartman", "Jake Middleton", "Brandon Duhaime", "Marco Rossi", "Joel Eriksson Ek", "Brock Faber", "Jon Merrill"]


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