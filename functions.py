"""
Course: CSE 251, week 14
File: functions.py
Author: Lily Brown

Instructions:

Depth First Search
https://www.youtube.com/watch?v=9RHO6jU--GU

Breadth First Search
https://www.youtube.com/watch?v=86g8jAQug04


Requesting a family from the server:
family_id = 6128784944
request = Request_thread(f'{TOP_API_URL}/family/{family_id}')
request.start()
request.join()

Example JSON returned from the server
{
    'id': 6128784944, 
    'husband_id': 2367673859,        # use with the Person API
    'wife_id': 2373686152,           # use with the Person API
    'children': [2380738417, 2185423094, 2192483455]    # use with the Person API
}

Requesting an individual from the server:
person_id = 2373686152
request = Request_thread(f'{TOP_API_URL}/person/{person_id}')
request.start()
request.join()

Example JSON returned from the server
{
    'id': 2373686152, 
    'name': 'Stella', 
    'birth': '9-3-1846', 
    'parent_id': 5428641880,   # use with the Family API
    'family_id': 6128784944    # use with the Family API
}

You will lose 10% if you don't detail your part 1 and part 2 code below

Describe how to speed up part 1

To speed up part 1, threads are used both for adding the children, and searching for the next grandparent to check on the tree. Also, to prevent the program from spending extra time running if an ID is invalid or blank, the ID is checked to make sure it's real before the program continues.

Describe how to speed up part 2

To speed up part 2, threads are used once again for adding the children. Threads are also used for running through the queue for the next ID to check, in a similar fashion to how the recursion was used for the depth search, Also, just like in the depth search, the program makes sure to check if an ID is valid before running any code for it.

Extra (Optional) 10% Bonus to speed up part 3

N/A

"""
from common import *
import queue

# -----------------------------------------------------------------------------
def depth_fs_pedigree(family_id, tree):
    # KEEP this function even if you don't implement it
    # TODO - implement Depth first retrieval
    # TODO - Printing out people and families that are retrieved from the server will help debugging

    if not family_id:
        return
    
    request_family = Request_thread(f'{TOP_API_URL}/family/{family_id}')
    request_family.start()
    request_family.join()

    family = Family(request_family.get_response())
    
    tree.add_family(family)

    if family.get_husband():
        request_husband = Request_thread(f'{TOP_API_URL}/person/{family.get_husband()}')
        request_husband.start()
        request_husband.join()

        husband = Person(request_husband.get_response())

        tree.add_person(husband)

    if family.get_wife():
        request_wife = Request_thread(f'{TOP_API_URL}/person/{family.get_wife()}')
        request_wife.start()
        request_wife.join()

        wife = Person(request_wife.get_response())

        tree.add_person(wife)

    if family.get_children():
        request_children = []
        for get_child in family.get_children():
            if tree.get_person(get_child) == None:
                request_child = Request_thread(f'{TOP_API_URL}/person/{get_child}')
                request_children.append(request_child)
                request_child.start()

        for request_child in request_children:
            request_child.join()

            child = Person(request_child.get_response())

            tree.add_person(child)

    threads = []

    if husband.get_parentid():
        if tree.get_person(husband.get_parentid()) == None:
            thread = threading.Thread(target=depth_fs_pedigree, args=(husband.get_parentid(), tree))
            threads.append(thread)
            thread.start()

    if wife.get_parentid():
        if tree.get_person(wife.get_parentid()) == None:
            thread = threading.Thread(target=depth_fs_pedigree, args=(wife.get_parentid(), tree))
            threads.append(thread)
            thread.start()
    
    for thread in threads:
        thread.join()

    return

# -----------------------------------------------------------------------------
def breadth_fs_pedigree(family_id, tree):
    # KEEP this function even if you don't implement it
    # TODO - implement breadth first retrieval
    # TODO - Printing out people and families that are retrieved from the server will help debugging

    if not family_id:
        return
    
    q = queue.Queue()

    q.put(family_id)

    def breadth_fs_helper(family_id):

        nonlocal tree
        nonlocal q

        request_family = Request_thread(f'{TOP_API_URL}/family/{family_id}')
        request_family.start()
        request_family.join()

        family = Family(request_family.get_response())
        
        tree.add_family(family)

        if family.get_husband():
            request_husband = Request_thread(f'{TOP_API_URL}/person/{family.get_husband()}')
            request_husband.start()
            request_husband.join()

            husband = Person(request_husband.get_response())

            tree.add_person(husband)

            if husband.get_parentid():
                if tree.get_person(husband.get_parentid()) == None:
                    q.put(husband.get_parentid())

        if family.get_wife():
            request_wife = Request_thread(f'{TOP_API_URL}/person/{family.get_wife()}')
            request_wife.start()
            request_wife.join()

            wife = Person(request_wife.get_response())

            tree.add_person(wife)

            if wife.get_parentid():
                if tree.get_person(wife.get_parentid()) == None:
                    q.put(wife.get_parentid())

        if family.get_children():
            request_children = []
            for get_child in family.get_children():
                if tree.get_person(get_child) == None:
                    request_child = Request_thread(f'{TOP_API_URL}/person/{get_child}')
                    request_children.append(request_child)
                    request_child.start()

            for request_child in request_children:
                request_child.join()

                child = Person(request_child.get_response())

                tree.add_person(child)

    while q.qsize() > 0:
        families = []

        for _ in range(q.qsize()):
            next_family = threading.Thread(target=breadth_fs_helper, args=(q.get(),))
            families.append(next_family)
            next_family.start()

        for family in families:
            family.join()

    return

# -----------------------------------------------------------------------------
def breadth_fs_pedigree_limit5(family_id, tree):
    # KEEP this function even if you don't implement it
    # TODO - implement breadth first retrieval
    #      - Limit number of concurrent connections to the FS server to 5
    # TODO - Printing out people and families that are retrieved from the server will help debugging

    if not family_id:
        return

    pass