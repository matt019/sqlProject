from enum import Enum
import datetime
import mysql.connector
from mysql.connector import Error

#def preparedStatement(statement):
#    cursor = cnx.cursor()
#    sql = (statement)
#    cursor.execute(sql)
#    resultSet = cursor.fetchall()
#    i=1
#    for row in resultSet:
#        print(str(i) + ') ' + row[0])
#        i += 1
#    cursor.close

def callStoredProcedure(storedProcedure, args=()):
    cnx = None
    try: 
        cnx = mysql.connector.connect(user='root', 
                                       password='Korra1996!',
                                       host='localhost',
                                       database='library')
        if cnx.is_connected():
            cursor = cnx.cursor()
            cursor.callproc(storedProcedure, args)   
    except Error as e:
        global activeState
        activeState = State.MAIN
        print("Unable to connect to the library system.\n MySQL connection error", e)
        exit()
    finally:
        if cnx: 
            cnx.commit()
            cursor.close()
            cnx.close()

def getQueryColumn(storedProcedure, column, args=()): 
    cnx = None
    try: 
        cnx = mysql.connector.connect(user='root', 
                                       password='Korra1996!',
                                       host='localhost',
                                       database='library')
        if cnx.is_connected():
            cursor = cnx.cursor()
            cursor.callproc(storedProcedure, args)                              
            for result in cursor.stored_results():
                resultAsList = []
                for columnIndex in result.fetchall():
                    resultAsList.append(columnIndex[column])
                return resultAsList
    except Error as e:
        print("Unable to connect to the library system.\n MySQL connection error", e)
        global activeState
        activeState = State.MAIN
        exit()
    finally:
        if cnx:
            cursor.close()
            cnx.close()

def listCombiner(list1, list2, joinForm):
    combinedList = []
    for itemA, itemB in zip(list1, list2):
        combinedList.append(itemA + joinForm + itemB)
    return combinedList

def displayResultSet(resultSet, quitMenu=False):
    i=1
    for result in resultSet:
        print(str(i) + ') ' + str(result))
        i += 1
    if quitMenu == True:
        print(str(i) + ') Quit to menu?')    

def validateInt(prompt=''):
    while True:
        if prompt:
           validatable = input(prompt) 
        else: 
            validatable = input()

        try:
            validated = int(validatable)
            if validated < 0:  
                print('Input must be a non-negative integer, try again')
                continue
            return validated
        except ValueError:
            print('Input must consist solely of only numbers')  

def validateString(prompt=''):
    while True:
        if prompt:
            validatable = input(prompt) 
        else: 
            validatable = input()

        if not validatable:  
            print('Input must be a non-empty string')
            continue
        return validatable    

def validateDate():   
    while True:
        date = input('Enter new due date: ')  
        try:
            validatedDate = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            return validatedDate  
        except ValueError:
            print("Incorrect date format, should be YYYY-MM-DD HH:MM:SS")

def getValidInput(validLength):
    while True:
        try:
            userSelection = int(input())
        except ValueError:
            print('Please make your selection using the number pad.')  
            continue
        if (userSelection < 1) or (userSelection > validLength):
            print('Please select a value in the numbered list.') 
            continue
        else:
            break
    return userSelection
            
class State(Enum):
    MAIN = 1
    LIB1 = 2
    LIB2 = 3
    LIB3 = 4
    BORR1 = 5
    BORR2 = 6
    ADMIN =  7

def libraryMenuHandler(screenCode):
    case={
        State.MAIN: main,
        State.LIB1: lib1,
        State.LIB2: lib2,
        State.LIB3: lib3,
        State.BORR1: borr1,
        State.ADMIN: admin
        }
    case.get(screenCode, State.MAIN)()

def main():
    def selectionHandler(user):
        return {
            1: State.LIB1,
            2: State.ADMIN,
            3: State.BORR1
        }.get(user, State.MAIN)

    print("Welcome to the GCIT Library Management System. Which category of a user are you?\n")
    print("1) Librarian \n2) Administrator \n3) Borrower \n")

    global activeState
    activeState = selectionHandler(getValidInput(3))
    return (activeState)       

def lib1():
    def selectionHandler(selection):
        return {
            1: State.LIB2,
            2: State.MAIN
        }.get(selection, State.LIB1)

    print("1) Enter Branch you manage \n2) Quit to previous \n")
    global activeState
    activeState = selectionHandler(getValidInput(2))
    return (activeState)

def lib2():
    branchNameList = getQueryColumn('getBranches', 0)
    branchAddressList = getQueryColumn('getBranches', 1)
    displayResultSet(listCombiner(branchNameList, branchAddressList, ', '), True)


    userSelection = getValidInput(len(branchNameList)+1)

    global activeState

    if userSelection == (len(branchNameList)+1):
        activeState = State.LIB1
        return(activeState)
    else:
        activeState = State.LIB3
        lib3(branchNameList[userSelection-1], branchAddressList[userSelection-1])

def lib3(name, address):
    branchName = name
    branchAddress = address
    branchId = getQueryColumn('getBranchId', 0, (branchName, branchAddress))[0]

    global activeState

    while activeState == State.LIB3:
        print('1) Update the details of the Library \n2) Add copies of a Book to the Branch \n3) Quit to previous \n')
        userSelection = getValidInput(3)

        if userSelection == 1:
            print('You have chosen to update the Branch with Branch Id: '+str(branchId) +' and Branch Name: '+branchName+'.\nEnter \'quit\' at any prompt to cancel operation\n')
            print('Please enter new branch name or enter N/A for no change:')

            userSelection = input()

            updatedBranchName=''
            if userSelection=='quit':
                continue
            else:
                if userSelection=='N/A':
                    updatedBranchName = ''
                else:
                    updatedBranchName = userSelection

                print('Please enter new branch address or enter N/A for no change:')
                userSelection = input()  

                if userSelection=='quit':
                    continue
                elif userSelection=='N/A':
                    pass
                else:
                    branchAddress = userSelection
                if updatedBranchName:
                    branchName = updatedBranchName
            
            callStoredProcedure('updateBranch', (branchName, branchAddress, branchId))

        elif userSelection ==2:
            bookTitlesList = getQueryColumn('getAllBooks',0)
            bookAuthorsList = getQueryColumn('getAllBooks',1)

            print('Pick the Book you want to add copies of to your branch:\n')
            displayResultSet(listCombiner(bookTitlesList, bookAuthorsList, ' by '), True)

            userSelection = getValidInput(len(bookTitlesList)+1)
            if userSelection == (len(bookTitlesList)+1):
                continue

            bookId = getQueryColumn('getBookID', 0, (bookTitlesList[userSelection-1], bookAuthorsList[userSelection-1]))[0]

            numCopiesList = getQueryColumn('getNumCopies', 0, (branchId, bookId))
            if numCopiesList:
                numCopies = numCopiesList[0]
            else:
                numCopies = 0    

            print('Existing number of copies: '+ str(numCopies)+'\n')

            print('Enter new number of copies: \n')
            validatedCopies = validateInt()
   
            
            callStoredProcedure('updateNumCopies', (bookId, branchId, validatedCopies))

        else:
            activeState = State.LIB2
            return(activeState)

def borr1():
    print('Enter your Card Number:\n')
    cardNo = validateInt()
    while cardNo not in getQueryColumn('getBorrowerCardNumbers', 0):
        print('That card number is not in our system. Please enter a valid card number number:\n')
        cardNo = validateInt()

    global activeState

    while True:
        print('1) Check out a book\n2) Return a book\n3) Quit to previous \n')
        userSeleciton = getValidInput(3)
        
        ##CHECKOUT BOOKS
        if userSeleciton == 1:
            branchNameList = getQueryColumn('getBranches',0)
            branchAddressList = getQueryColumn('getBranches',1)

            displayResultSet(listCombiner(branchNameList, branchAddressList, ', '), True)
            print('Pick the Branch you want to check out from:')

            userSelection = getValidInput(len(branchNameList)+1)

            branchName = branchNameList[userSelection-1]
            branchAddress = branchAddressList[userSelection-1]

            if userSelection == (len(branchNameList)+1):
                activeState = State.BORR1
                return(activeState)
            else:
                branchId = getQueryColumn('getBranchId', 0, (branchName, branchAddress))[0]

                bookTitlesList = getQueryColumn('getBooksBranch', 0, (branchId,))
                bookAuthorsList = getQueryColumn('getBooksBranch', 1, (branchId,))

                displayResultSet(listCombiner(bookTitlesList, bookAuthorsList, ' by '), True)
                print('Pick the Book you want to check out:\n')

                userSelection = getValidInput(len(bookTitlesList)+1)
                if userSelection == (len(bookTitlesList)+1):
                    continue

                bookId = getQueryColumn('getBookID', 0, (bookTitlesList[userSelection-1], bookAuthorsList[userSelection-1]))[0]

                callStoredProcedure('checkOutBook', (bookId, branchId, cardNo))
                print('Book checkout complete.')

    ##RETURN BOOKS

        elif userSeleciton == 2:
            branchNameList = getQueryColumn('getBranches',0)
            branchAddressList = getQueryColumn('getBranches',1)
            displayResultSet(listCombiner(branchNameList, branchAddressList, ', '), True)

            print('\nPick the Branch you want to return to:')

            userSelection = getValidInput(len(branchNameList)+1)

            branchName = branchNameList[userSelection-1]
            branchAddress = branchAddressList[userSelection-1]

            if userSelection == (len(branchNameList)+1):
                activeState = State.BORR1
                return(activeState)
            else:
                branchId = getQueryColumn('getBranchId', 0, (branchName, branchAddress))[0]

                bookTitlesList = getQueryColumn('getBorrLoansFromBr', 0, (cardNo, branchId))
                bookAuthorsList = getQueryColumn('getBorrLoansFromBr', 1, (cardNo, branchId,))

                print('Pick the Book you want to return:\n')
                displayResultSet(listCombiner(bookTitlesList, bookAuthorsList, ' by '), True)

                userSelection = getValidInput(len(bookTitlesList)+1)
                if userSelection == (len(bookTitlesList)+1):
                    continue

                bookId = getQueryColumn('getBookId', 0, (bookTitlesList[userSelection-1], bookAuthorsList[userSelection-1]))[0]

                callStoredProcedure('returnBook', (bookId, branchId, cardNo))
                print('Book return complete.')
        else:
            activeState = State.MAIN
            return(activeState)

def admin():  
    print('----- Administrator console -----\n') 
    print('1) Add/Update/Delete Book and Author')
    print('2) Add/Update/Delete Publishers')
    print('3) Add/Update/Delete Library Branches')
    print('4) Add/Update/Delete Borrwers')
    print('5) Over-ride Due Date for a Book Loan')
    print('6) Quit to menu')
    
    userSelection = getValidInput(6)
    global activeState

    ##BOOK AUTHOR UPDATES##
    if userSelection == 1:
        print('1) Add Book and Author:')
        print('2) Update Book and Author:')
        print('3) Delete Book and Author:')

        userSelection = getValidInput(3)

        if userSelection == 1:
            bookTitle = validateString('Enter book title: ')

            print('1) Choose an existing author \n2) Enter new author')
            userSelection = getValidInput(2)
            if userSelection == 1:
                authorsList = getQueryColumn('getAllAuthors', 0)
                displayResultSet(authorsList, True)
                userSelection = getValidInput(len(authorsList)+1)
                if userSelection == (len(authorsList)+1):
                    activeState = State.ADMIN
                    return(activeState)                                   
                authorId = getQueryColumn('getAuthorId', 0, (authorsList[userSelection-1],))[0]
                bookPublisherId = validateInt('Enter book publisher ID: ')
                callStoredProcedure('adminAddNewBookOldAuth', (bookTitle, bookPublisherId, authorId))
            else:
                bookAuthor = validateString('Enter author name: ')
                bookPublisherId = validateInt('Enter book publisher ID: ')
                callStoredProcedure('adminAddNewBA', (bookTitle, bookAuthor, bookPublisherId))

        elif userSelection == 2:
            bookId = validateInt('Enter book ID: ')
            authorId = validateInt('Enter author ID: ')
            bookTitle = validateString('Enter new book title: ')
            bookAuthor = validateString('Enter new book author: ')
            bookPublisherId = validateInt('Enter book publisher ID: ')
            callStoredProcedure('adminUpdateBa', (bookId, authorId, bookPublisherId, bookAuthor, bookTitle))

        elif userSelection == 3:
            bookId = validateInt('Enter book ID: ')
            authorId = validateInt('Enter author ID: ') 
            callStoredProcedure('adminDeleteBa', (bookId, authorId))
        
    ### PUBLISHERS UPDATES ###
    elif userSelection == 2:
        print('1) Add Publishers:')
        print('2) Update Publishers:')
        print('3) Delete Publishers:')

        userSelection = getValidInput(3)

        if userSelection == 1:
            publisherName = validateString('Enter publisher name: ')
            publisherAddress = validateString('Enter publisher address: ')
            publisherPhone = validateInt('Enter publisher phone number: ')
            callStoredProcedure('adminAddPub', (publisherName, publisherAddress, publisherPhone))

        elif userSelection == 2:
            publisherId = validateInt('Enter publisher ID: ')
            publisherName = validateString('Enter new publisher name: ')
            publisherAddress = validateString('Enter new publisher address: ')
            publisherPhone = validateInt('Enter new publisher phone: ')
            callStoredProcedure('adminUpdatePub', (publisherId, publisherName, publisherAddress, publisherPhone))

        elif userSelection == 3:
            publisherId = validateInt('Enter publisher ID: ')
            callStoredProcedure('adminDeletePub', (publisherId,))

    ## BRANCH UPDATES ##
    elif userSelection == 3:
        print('1) Add Library Branches:')
        print('2) Update Library Branches:')
        print('3) Delete Library Branches:')

        userSelection = getValidInput(3)

        if userSelection == 1:
            branchName = validateString('Enter branch name: ')
            branchAddress = validateString('Enter branch address: ')
            callStoredProcedure('adminAddBr', (branchName, branchAddress))

        elif userSelection == 2:
            branchId = validateInt('Enter branch ID: ')
            branchName = validateString('Enter new branch name: ')
            branchAddress = validateString('Enter new branch address: ')
            callStoredProcedure('adminUpdateBr', (branchId, branchName, branchAddress))

        elif userSelection == 3:
            branchId = validateInt('Enter branch ID: ')
            callStoredProcedure('adminDeleteBr', (branchId,))    

    ## BORROWERS UPDATES ##
    elif userSelection == 4:
        print('1) Add Borrowers:')
        print('2) Update Borrowers:')
        print('3) Delete Borrowers:')

        userSelection = getValidInput(3)

        if userSelection == 1:
            borrowerName = validateString('Enter borrower name: ')
            borrowerAddress = validateString('Enter borrower address: ')
            borrowerPhone = validateInt('Enter borrower phone: ')
            callStoredProcedure('adminAddBorr', (borrowerName, borrowerAddress, borrowerPhone))

        elif userSelection == 2:
            cardNo = validateInt('Enter borrower card number: ')
            borrowerName = validateString('Enter borrower name: ')
            borrowerAddress = validateString('Enter borrower address: ')
            borrowerPhone = validateInt('Enter borrower phone: ')
            callStoredProcedure('adminUpdateBorr', (cardNo, borrowerName, borrowerAddress, borrowerPhone))

        elif userSelection == 3:
            cardNo = validateInt('Enter borrower card number: ')
            callStoredProcedure('adminDeleteBorr', (cardNo,))            

    ### DUE DATE UPDATES##
    elif userSelection == 5:
        bookId = validateInt('Enter bookId: ')
        branchId = validateInt('Enter branchId: ')
        cardNo = validateInt('Enter cardNo: ')
        dueDate = validateDate()   
        
        callStoredProcedure('overrideDueDate', (bookId, branchId, cardNo, dueDate))
    else:
        activeState = State.MAIN
        return activeState

def libraryManagementSystemApplication():
    while True:
        libraryMenuHandler(activeState)

activeState = State.MAIN
libraryManagementSystemApplication()