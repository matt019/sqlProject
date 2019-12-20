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

def getQueryColumn(storedProcedure, columnNumber): 
    cursor = cnx.cursor()
    cursor.callproc(storedProcedure)
    for result in cursor.stored_results():
        resultAsList = []
        for columnIndex in result.fetchall():
            resultAsList.append(columnIndex[columnNumber])
        return resultAsList
    cursor.close

def listCombiner(list1, list2):
    combinedList = []
    for itemA, itemB in zip(list1, list2):
        combinedList.append(itemA + ', '+ itemB)
    return combinedList

def displayResultSet(resultSet, quitMenu=False):
    i=1
    for result in resultSet:
        print(str(i) + ') ' + result)
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
        #'lib3': lib3,
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
    branchNameList = getQueryColumn('getBranchNames', 0)
    branchAddressList = getQueryColumn('getBranchAddress', 0)
    displayResultSet(listCombiner(branchNameList, branchAddressList), True)

    print(branchNameList)
    userSelection = getValidInput(len(branchNameList)+1)

    if userSelection == (len(branchNameList)+1):
        global activeState
        activeState = State.LIB1
        return(activeState)
    else:
        lib3(branchNameList[userSelection-1], branchAddressList[userSelection-1])

def lib3(branchName, branchAddress):
    global activeState 
    activeState = State.LIB3
    print('1) Update the details of the Library \n2) Add copies of Book to the Branch \nQuit to previous \n')
    
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

#preparedStatement('Select branchname from tbl_library_branch')
#print('---------SINGLE DATA COLUMN TEST-------------')
#displayResultSet(getQueryColumn('getBranches', 0), True)

##### FIX NESTED FUNCTION CALLS -> state maybe##########
cnx.close()