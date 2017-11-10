import discord
import random
import datetime
import re
import discord_token

raffle_id = 1


def get_raffle_id():
    global raffle_id
    value = raffle_id
    raffle_id += 1
    return value


class Ticket:
    def __init__(self, discord_user: discord.Member):
        self.user = discord_user

    def __str__(self):
        return "%s's ticket" % self.user.display_name

    def __repr__(self):
        return self.__str__()

    def get_id(self):
        return self.user.id

    def get_username(self):
        return self.user.display_name


class Raffle:
    # The Raffle class stores the following:
    # - the reward description
    # - the date at which a raffle must occur
    # - whether or not this raffle has been completed or not
    # - a list of raffle tickets
    # - when a raffle is conducted, a winner must be known
    def __init__(self, reward: str, date: datetime.date):
        self.id = get_raffle_id()
        self.reward_description = reward
        self.tickets = []
        self.date_of_raffle = date
        self.is_completed = False
        self.winner = None  # Discord user Display Name

    # get_number_of_tickets() lets us know how many users have entered this raffle
    def get_number_of_tickets(self):
        return len(self.tickets)

    # add_ticket() accepts a ticket object and attempts to include the ticket
    # in this raffle. If the user associated with the raffle is already within the list
    # of raffle tickets, we do not include another ticket.
    # returns True if ticket is accepted, False otherwise
    def add_ticket(self, new_ticket: Ticket):
        for ticket in self.tickets:
            if ticket.get_id() == new_ticket.get_id():
                return False
        self.tickets.append(new_ticket)
        return True

    # conduct_raffle() attempts to conduct a raffle.
    # if the function is called before the date of the raffle, nothing is done.
    # else,
    # 1) get a random index
    # 2) shuffle the list of tickets
    # 3) draw with the random index and determine the winner
    def conduct_raffle(self):
        if datetime.date.today() < self.date_of_raffle:
            return False
        else:
            index = random.randrange(len(self.tickets))
            random.shuffle(self.tickets)
            self.winner = (self.tickets[index]).get_username()
            self.is_completed = True
            return True

    def raffle_details(self):
        if self.is_completed:
            return 'ID: %d; %s; Completed on %s' % (self.id, self.reward_description, self.date_of_raffle)
        else:
            return 'ID: %d; %s; To be completed on %s' % (self.id, self.reward_description, self.date_of_raffle)

    def __str__(self):
        if self.is_completed:
            return "%d: %s rewarded to %s on %s" % (self.id, self.reward_description, self.winner, self.date_of_raffle)
        else:
            return "%d: %s" % (self.id, self.reward_description)

    def __repr__(self):
        return self.__str__()


# ==================================================================================================================
# Actual bot
# ==================================================================================================================
client: discord.Client = discord.Client()
raffles = []  # a list of raffles that our bot uses
time = datetime.time(hour=10, minute=0, second=0)
pattern = re.compile('[0-3]?[0-9]/[0-3]?[0-9]/20[1-2][0-9]')


# define functions to interact with our list of raffles

# get_new_raffle() takes in a description and a date (as a string) and
# returns a new raffle object
# assumes that the date string is formatted mm/dd/yyyy
# let user input handler deal with invalid input
async def get_new_raffle(description: str, date_of_raffle: str):
    date_parts = date_of_raffle.split("/")  # '/' char is the delimiter
    year = int(date_parts[2])
    month = int(date_parts[0])
    day = int(date_parts[1])
    date = datetime.date(year, month, day)
    await Raffle(description, date)


# compares an ID to a given Raffle to see if the ID's match
def raffle_id_matches(search_id: int, raffle: Raffle):
    return search_id == raffle.id


# searches through the raffles list to get a given Raffle based on ID
# returns None if it does not exist
async def get_raffle_by_id(search_id: int):
    for raffle in raffles:
        if raffle_id_matches(search_id, raffle):
            await raffle
    await None


@client.event
async def on_ready():
    print('Username: ' + client.user.name)
    print('ID: ' + client.user.id)


# different branches
# if no arguments are given, we print out a help suggestion
# else, base operations off of 1st argument
# 'list' => list out all of the raffles by ID
# - no subcommands
# 'help' => lists all of the available commands
# - no subcommands
# 'new' => create a new raffle
# - must specify a name and date. see new_raffle_usage_message()
# 'delete' => deletes a raffle
# - must specify a raffle ID
# 'details' => prints out the details of a given raffle
# - must specify a raffle ID
# 'run' => conducts any raffle that hasn't been done yet
# - no subcommands
@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return  # we want to filter out messages from our bot
    if message.content.startswith('!raffle'):
        message_items = message.content.split()
        channel: discord.Channel = message.channel
        if len(message_items) < 2:
            await client.send_message(channel, raffle_invalid_message())
        else:
            if message_items[1] == 'list':
                await client.send_message(channel, list_raffles())
            elif message_items[1] == 'help':
                await client.send_message(channel, raffle_help_message())
            elif message_items[1] == 'new':
                # validate the number of args,
                # then validate the date formatting
                if len(message_items) < 4:
                    await client.send_message(channel, new_raffle_usage_message())
                else:
                    # check format of date parameter
                    date_param: str = message_items[2]
                    date_is_validated = False
                    try:
                        datetime.datetime.strptime(date_param, '%m/%d/%Y')
                        date_is_validated = True
                    except ValueError:
                        await client.send_message(channel, 'Date should be formatted MM/DD/YYYY')
                    if date_is_validated:
                        # no need for an else clause because if it wasn't validated, the except block catches that
                        parts_of_date = date_param.split('/')
                        year = int(parts_of_date[2])
                        month = int(parts_of_date[0])
                        day = int(parts_of_date[1])
                        date_of_raffle = datetime.date(year, month, day)
                        # now we need to extract the reward description from the rest of the message contents
                        # len("!raffle new mm/dd/yyyy " = 23
                        reward: str = message.content[23:]
                        new_raffle = Raffle(reward, date_of_raffle)
                        raffles.append(new_raffle)
                        await client.send_message(channel, 'New Raffle => (%s)' % new_raffle)
                pass
            elif message_items[1] == 'delete':
                # if we are trying to delete a raffle, we must supply the ID of the raffle
                # first check validity of the argument
                id_arg: str = message_items[2]
                if id_arg.isdigit():
                    search_id = int(id_arg)
                    raffle_list_size_before = len(raffles)
                    # https://stackoverflow.com/questions/1207406/remove-items-from-a-list-while-iterating
                    raffles[:] = [raffle for raffle in raffles if raffle_id_matches(search_id, raffle)]
                    raffle_list_size_after = len(raffles)
                    if raffle_list_size_before > raffle_list_size_after:
                        await client.send_message(channel, 'Deleted raffle with ID = %d' % search_id)
                    else:
                        await client.send_message(channel, no_raffle_found_with_id(search_id))
                else:
                    await client.send_message(channel, delete_raffle_usage_message())
            elif message_items[1] == 'details':
                # if we are trying to list the details of a raffle, we must supply the ID of the raffle
                # check validity of the argument
                id_arg: str = message_items[2]
                if id_arg.isdigit():
                    search_id = int(id_arg)
                    found_raffle: Raffle = get_raffle_by_id(search_id)
                    if found_raffle is not None:
                        await client.send_message(channel, found_raffle.raffle_details())
                    else:
                        await client.send_message(channel, no_raffle_found_with_id(search_id))
                else:
                    await client.send_message(channel, details_raffle_usage_message())
            elif message_items[1] == 'run':
                # we want to run all of the available raffles for today
                # this means we want to check all raffles before TOMORROW
                tomorrow: datetime.date = datetime.date.today() + datetime.timedelta(days=1)
                for raffle in raffles:
                    if raffle.date_of_raffle < tomorrow and not raffle.is_completed:
                        raffle.conduct_raffle()
            else:
                await client.send_message(channel, raffle_help_message())


def new_raffle_usage_message():
    return 'New Raffle usage: !raffle new mm/dd/yyyy reward name'


# called when no arguments are given for the !raffle command
def raffle_invalid_message():
    return 'Usage: !raffle command [sub-commands]\n' \
           'Do "!raffle help" to list available commands'


def raffle_help_message():
    return 'Available commands:\n' \
           '\thelp\n' \
           '\tlist\n' \
           '\tnew\n' \
           '\tdelete\n' \
           '\tdetails\n'


def list_raffles():
    # we can't return an empty string, so if our raffles list is empty, say so
    if len(raffles) < 1:
        return 'No raffles found'
    listing: str = ''
    for raffle in raffles:
        listing += str(raffle) + '\n'
    return listing


def delete_raffle_usage_message():
    return 'Delete Raffle usage: !raffle delete ID'


def details_raffle_usage_message():
    return 'Details Raffle usage: !raffle details ID'


def no_raffle_found_with_id(some_id):
    return 'No raffle found with ID = %d' % some_id


token = discord_token.token
# run the bot
client.run(token)
