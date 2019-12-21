from enum import Enum
import mysql.connector

cnx = mysql.connector.connect(user='root', password='Korra1996!',
                              host='localhost',
                              database='library')

def preparedStatement(statement):
    cursor = cnx.cursor()
    sql = (statement)
    cursor.execute(sql)
    resultSet = cursor.fetchall()
    i=1
    for row in resultSet:
        print(str(i) + ') ' + row[0])
        i += 1
    cursor.close

def callStoredProcedure(storedProcedure, args=()):
    cursor = cnx.cursor()
    cursor.callproc(storedProcedure, args)   
    cursor.close 

def getQueryColumn(storedProcedure, column, args=()): 
    cursor = cnx.cursor()
    cursor.callproc(storedProcedure, args)
    for result in cursor.stored_results():
        resultAsList = []
        for columnIndex in result.fetchall():
            resultAsList.append(columnIndex[column])
        return resultAsList
    cursor.close

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

def libMenuSelector(screenCode):
    case={
        State.MAIN: main,
        State.LIB1: lib1,
        State.LIB2: lib2,
        State.LIB3: lib3,
        #'borr1': borr1,
        #'borr2': borr2,
        #'admin': admin
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
    branchNameList = getQueryColumn('getBranchName',0)
    branchAddressList = getQueryColumn('getBranchAddress',0)
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
    global cnx

    while activeState == State.LIB3:
        print('1) Update the details of the Library \n2) Add copies of Book to the Branch \n3) Quit to previous \n')
        userSelection = getValidInput(3)

        if userSelection == 1:
            print('You have chosen to update the Branch with Branch Id: '+str(branchId) +' and Branch Name: '+branchName+'.\nEnter ‘quit’ at any prompt to cancel operation\n')
            print('Please enter new branch name or enter N/A for no change:')

            userSelection = input()

            if userSelection=='quit':
                return
            else:
                if userSelection=='N/A':
                    pass
                else:
                    branchName= userSelection
                print('Please enter new branch address or enter N/A for no change:')
                userSelection = input()    
                if userSelection=='quit':
                    return
                elif userSelection=='N/A':
                    pass
                else:
                    branchAddress = userSelection
                    print(branchAddress)
            
            callStoredProcedure('updateBrNameAndAddress', (branchName, branchAddress, branchId))
            cnx.commit()

        elif userSelection ==2:
            bookTitlesList = getQueryColumn('getAllBooks',0)
            bookAuthorsList = getQueryColumn('getAllBooks',1)

            print('Pick the Book you want to add copies of to your branch:\n')
            displayResultSet(listCombiner(bookTitlesList, bookAuthorsList, ' by '), True)

            userSelection = getValidInput(len(bookTitlesList)+1)
            if userSelection == (len(bookTitlesList)+1):
                return

            bookId = getQueryColumn('getBookID', 0, (bookTitlesList[userSelection-1], bookAuthorsList[userSelection-1]))[0]

            numCopies = getQueryColumn('getNumCopies', 0, (branchId, bookId))[0]
            print('Existing number of copies: '+ str(numCopies)+'\n')

            while True:
                copies = input('Enter new number of copies: \n')
                try:
                    validatedCopies = int(copies)
                    if validatedCopies < 0:  
                        print('Input must be a non-negative integer, try again')
                        continue
                    break
                except ValueError:
                    print('Input must be a non-negative integer, try again')     
            
            callStoredProcedure('updateNumCopies', (bookId, branchId, validatedCopies))
            cnx.commit()

        else:
            activeState = State.LIB2
            return(activeState)

    
def borr1():
    print('Welcome Borrower')
#def borr2():
def admin():  
    print('Welcome Admin')  

def libraryManagementSystemApplication():
    while True:
        libMenuSelector(activeState)

activeState = State.MAIN
libraryManagementSystemApplication()

#displayResultSet(getQueryColumn('getBranchId', ('University Library', 'Boston')))
#preparedStatement('Select branchname from tbl_library_branch')
#print('---------SINGLE DATA COLUMN TEST-------------')
#displayResultSet(getQueryColumn('getBranches', 0), True)

##### FIX NESTED FUNCTION CALLS -> state maybe##########
cnx.close()