#!/usr/bin/env python

LP_PROJECT = "fuel"
LP_TAG = ""
LP_CACHEDIR = "./"

FUEL_LIBRARY = "fuel-library"

#TRELLO_BOARD = 'EnhTest'
TRELLO_BOARD = 'Enhancements Team'
TRELLO_LIST_NEW = 'Backlog/To Sort Out'
#TRELLO_LIST_NEW = 'Triage Queue'
#TRELLO_LIST_CONFIRMED = 'Backlog'
#TRELLO_LIST_CONFIRMED = 'Inbox/Todo'
#TRELLO_LIST_CONFIRMED_USER = 'In Progress'
#TRELLO_LIST_CONFIRMED_USER = 'Research/Design'
TRELLO_LIST_TRIAGED = 'Inbox/Todo'
TRELLO_LIST_TRIAGED_USER = 'Doing/Implementation'
TRELLO_LIST_IN_PROGRESS = 'On Review'
TRELLO_LIST_FIX_COMMITED = 'QA/Verification'
TRELLO_LIST_FIX_RELEASED = 'Done'

# Get Trello key and secret from https://trello.com/app-key
TRELLO_KEY = ""
TRELLO_SECRET = ""

# Open in browser
# https://trello.com/1/authorize?key=&name=Fuel-Library&expiration=never&response_type=token&scope=read,write
# to get the token. token should be READ and WRITE and should NEVER expire
TRELLO_TOKEN = ""

import itertools
import datetime
import re
from launchpadlib.launchpad import Launchpad
# from launchpadlib.credentials import Credentials
from trello import TrelloClient


def describe(object):
    print 'collections:'
    print object.lp_collections
    print 'entries:'
    print object.lp_entries
    print 'attibutes:'
    print object.lp_attributes
    print 'operations:'
    print object.lp_operations


def get_trello_list(lists, name):
    list = [list for list in lists if list.name == name]
    if len(list) == 0:
        print "No Trello list found" + name
        exit(0)
    return list[0]
IMP_2_LABEL = {'High': 'orange',
               'Critical': 'red',
               'Medium': 'yellow',
               'Low': 'purple',
               'Wishlist': 'blue',
               'Undecided': 'blue',
               'Unknown': 'blue'}

MAP_USER_LP_2_TR = {"fuel-library": "fuellibrary",
                    "ashtokolov": "ashtokolov",
                    }


def lp2tr(lp_name):
    try:
        tr_id = tr.get_member(MAP_USER_LP_2_TR[lp_name]).id
    except:
        tr_id = tr.get_member("ashtokolov").id
    return tr_id

print 'Sync started at:', datetime.datetime.now()

# login to lauchpad
lp = Launchpad.login_anonymously('test', 'production', LP_CACHEDIR)

# login to trello
tr = TrelloClient(api_key=TRELLO_KEY, api_secret=TRELLO_SECRET, token=TRELLO_TOKEN, token_secret=TRELLO_SECRET)

# Extract Trello board
all_boards = tr.list_boards()
boards = [board for board in all_boards if board.name == TRELLO_BOARD]
if len(boards) == 0:
    print "No Trello board found:" + TRELLO_BOARD
    exit(0)
board = boards[0]
print 'Found Board:', board
# , dir(board)

# Extract Trello lists
lists = board.open_lists()
list_new = get_trello_list(lists, TRELLO_LIST_NEW)
#list_confirmed = get_trello_list(lists, TRELLO_LIST_CONFIRMED)
#list_confirmed_user = get_trello_list(lists, TRELLO_LIST_CONFIRMED_USER)
list_in_progress = get_trello_list(lists, TRELLO_LIST_IN_PROGRESS)
list_triaged = get_trello_list(lists, TRELLO_LIST_TRIAGED)
list_triaged_user = get_trello_list(lists, TRELLO_LIST_TRIAGED_USER)
list_fix_commited = get_trello_list(lists, TRELLO_LIST_FIX_COMMITED)
list_fix_released = get_trello_list(lists, TRELLO_LIST_FIX_RELEASED)

##print 'Inbox/Todo:', list_confirmed
##print 'Research/Design:', list_confirmed_user
#print 'Doing/Implementation:', list_triaged_user
#print 'Review:', list_in_progress
#print 'QA Verification:', list_fix_commited
#print 'Done:', list_fix_released, list_fix_released.id
## print dir(list_done)

# Extract all the cards in all lists for specific trello board
bugs = dict()
cards = board.open_cards()
for card in cards:
    groups = re.search('(\d{7})', card.name)
    if not (groups is None):
        bugs[groups.group(0)] = card
#print 'Read Trelllo cards', bugs.keys()

# read Lauchpads project and its bugs
project = lp.projects[LP_PROJECT]
fueluser = lp.people("fuel-library")

# describe(project);
# try:
#    tasks = project.searchTasks()
# except:
#    print 'No bugs found'

# find new bugs and put to trello
userlist = []
userlist.append(fueluser.name)
for entrie in fueluser.members.entries:
    userlist.append(entrie['name'])

LP_STATUS = ["New", "Confirmed", "Triaged", "In Progress", "Fix Committed", "Fix Released"]
LP_MILESTONE = ["https://api.launchpad.net/1.0/fuel/+milestone/8.0"]
# LP_IMPORTANCE = ["High", "Critical"]
LP_IMPORTANCE = ["High", "Critical", "Medium", "Low", "Wishlist", "Low", "Undecided", "Unknown"]
BUG_LABEL = 'green'
HIGH_LABEL = 'orange'
CRITICAL_LABEL = 'red'

#for username in userlist:
#    user = lp.people(username)
series=project.series
series8=series[12]
#print 'Series', series8
seriestasks = series8.searchTasks(tags='feature',tags_combinator='All',
                                  importance=LP_IMPORTANCE, status=LP_STATUS,
                                  milestone=LP_MILESTONE,omit_targeted=False)
#
#

milestonetasks = project.searchTasks(tags="feature",
                             status=LP_STATUS,
                             milestone=LP_MILESTONE,
                             importance=LP_IMPORTANCE
                             #assignee='https://api.launchpad.net/1.0/~%s' % username
                             )
#    print username
tasks = itertools.chain(seriestasks, milestonetasks)
#print seriestasks.total_size + milestonetasks.total_size

for task in tasks:
        bug = task.bug
        bug_id = str(bug.id)
        print 'LP bug', bug_id #, bug.title, task.status, task.assignee
        try:
            username = task.assignee.name
        except:
            username = 'ashtokolov'
        lp_member_id = lp2tr(username)
        if not (bug_id in bugs):
            print 'Add to trello:', bug_id
            card = list_new.add_card('Bug '+bug_id+': '+task.bug.title, bug.web_link+'\n'+bug.description)
            card.client.fetch_json('/cards/{0}/idMembers'.format(card.id), http_method='PUT', post_args={'value': '{0}'.format(lp_member_id)})
            card.client.fetch_json('/cards/{0}/labels'.format(card.id), http_method='PUT', post_args={'value': IMP_2_LABEL[task.importance]})
            # card.assign(lp_member_id)
            bugs[bug_id] = card
        else:
            card = bugs[bug_id]
            try:
                tr_member_id = card.member_id
            except:
                tr_member_id = "ashtokolov"
            if card.desc != bug.web_link+'\n'+bug.description:
                card.client.fetch_json('/cards/{0}/desc'.format(card.id), http_method='PUT', post_args={'value': bug.web_link+'\n'+bug.description})
            if lp_member_id != tr_member_id[0] or len(tr_member_id) >= 2:
                print 'LP assignee differs'
                card.client.fetch_json('/cards/{0}/idMembers'.format(card.id), http_method='PUT', post_args={'value': '{0}'.format(lp_member_id)})
                # for member_id in tr_member_id:
                #    card.client.fetch_json('/cards/{0}/idMembers/{1}'.format(card.id, member_id), http_method='DELETE')
                # card.assign(lp_member_id)
            if card.labels[0]['color'] != IMP_2_LABEL[task.importance]:
                card.client.fetch_json('/cards/{0}/labels'.format(card.id), http_method='PUT',
                                       post_args={'value': IMP_2_LABEL[task.importance]})
        # print bug_id, task.status, task.assignee, card
        if task.web_link.find('fuel') != -1:
            if task.status == 'Fix Released':
                card.change_list(list_fix_released.id)
            elif task.status == 'Fix Committed':
                card.change_list(list_fix_commited.id)
            elif task.status == 'In Progress':
                card.change_list(list_in_progress.id)
            elif task.status == 'Triaged' and username == 'fuel-library':
                card.change_list(list_triaged.id)
            elif task.status == 'Triaged' and username == 'fuel-python':
                card.change_list(list_triaged.id)
            elif task.status == 'Triaged':
                card.change_list(list_triaged_user.id)
            elif task.status == 'Confirmed':
                card.change_list(list_new.id)
            elif task.status == 'New':
                card.change_list(list_new.id)

print "Done"

#
#
