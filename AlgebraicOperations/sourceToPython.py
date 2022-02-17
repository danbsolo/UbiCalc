from sys import exit

def main():
    sourceMath = "2(3)($frac{3[}2}#)($frac{3}{55}#)"
    print(solveSimpleExpression(sourceMath))


def solveSimpleExpression(sourceMath):
    # because the exec function is built weirdly and can't save locally, we're putting its values in a local dictionary for *local* use 
    execDict = {}

    # as the function says, converting sourceMath to pythonMath
    pythonMath = convertToPythonMath(sourceMath)

    try:
        # letting python itself do the expression with the help of exec (able to execute strings as if it were actual code)
        exec("execDict['result'] = " + pythonMath)
    except SyntaxError:
        print(f"SyntaxError.")
        exit(2)
    except NameError:
        print(f"SyntaxError.")
        exit(3)

    return execDict['result']


def convertToPythonMath(sourceMath):
    middleMath = spaceOutOperators(sourceMath) # this function will turn the string into a list of characters. Way easier to work with moving forward.
    middleMath = changeCharacters(middleMath)

    pythonMath = ''.join(middleMath)

    # # test print 
    # print(middleMath)
    # print(pythonMath)

    return pythonMath


def spaceOutOperators(sourceMath):
    # appending a space so spacing around a right bracket doesn't result in an IndexError when it's the last character
    sourceMath = list(sourceMath + " ")

    # will put spaces before and after the characters listed after the "in" operator
    i = 0
    while i != len(sourceMath):
        if sourceMath[i] in '÷×+-*/()^':
            if sourceMath[i + 1] != " ":
                sourceMath.insert(i + 1, " ")
            if sourceMath[i - 1] != " ":
                sourceMath.insert(i, " ")
                i += 1
        
        if ''.join(sourceMath[i : i + 5]) == "$frac":
            bracketPairs = findBracketPairs(sourceMath, "$", "#") # only works if $frac is the only thing to start with a $ and end with a #

            endIndex = sourceMath.index("#", i) # only works if no nested $fracs

            fractionSubString = sourceMath[i:endIndex+1] # ['$', 'f', 'r', 'a', 'c', '{', '1', ' ', '+', ' ', '2', '}', '{', '2', '}', '#']
            fractionSubString = ''.join(fractionSubString) # $frac{1 + 2}{2}#

            standaloneNumberError(fractionSubString) # error check here

            if not bracketPairs:
                print("SyntaxError: $frac statement not ended with #.")
                exit(4)

            fractionSubString = fractionSubString.split() # ['$frac{1', '+', '2}{2}#']
            fractionSubString = ''.join(fractionSubString) # $frac{1+2}{2}#

            # replacing the dollar sign with the whole fractionSubString
            sourceMath.insert(i, fractionSubString)

            for j in range(i + 1, endIndex + 2):
                sourceMath[j] = " "
            # print(sourceMath_example) -> ['3', ' ', '+', ' ', '$frac{1+2}{2}#', ' ', ' ', ' ', ' ', ' ', ' ', '-', ' ', '3', ' ']

            i = endIndex # we didn't delete anything, so this can freely skip to endIndex without worry
        i += 1


    # will join everything into one conjoined patty (includes spaces), then splits them to remove the spaces
    # this is identical to looping over the list and removing spaces
    sourceMath = ''.join(sourceMath)
    return sourceMath.split()


def changeCharacters(sourceMath):
    i = 0

    while i != len(sourceMath):
        # just replaces human notation with python notation
        if sourceMath[i] == "^":
            sourceMath[i] = "**"
        if sourceMath[i] == "×":
            sourceMath[i] = "*"
        if sourceMath[i] == "÷":
            sourceMath[i] = "/"

        
        if sourceMath[i][0:5] == "$frac": # a "$frac" denotes a fraction of expressions
            bracketPairs = findBracketPairs(sourceMath[i], "{", "}")

            if not bracketPairs:
                print("SyntaxError: Curly braces out of line.")
                exit(4)

            expressions = []

            for leftBracket, rightBracket in bracketPairs:
                expressions.append(solveSimpleExpression(sourceMath[i][leftBracket + 1 : rightBracket])) # [['1', '*', '2'], ['2']]
            
            total = expressions[0]
            for express in expressions[1:]:
                total /= express

            if float(total) == int(total):  # basically, if the mantissa is just a 0, convert it into an integer
                sourceMath[i] = str(int(total))
            else:
                sourceMath[i] = str(total)


        if sourceMath[i] == "(" and (sourceMath[i - 1] == ")" or isNumber(sourceMath[i - 1])): # In human math, multiplication shortcuts exist such as "3(2+2)" or "(5)(3-1)"
                sourceMath.insert(i, "*") # if it's a number, adjust it for pythonMath
                i += 1 # have to add 1 to i again as we just inserted, pushing everything up by 1


        i += 1

    # Hard to explain, erm... Basically, sourceMath looks like this right now: ['2', '+', '3'], so changing it into '2 + 3' shouldn't error.
    # It will only error if sourceMath were like this: ['2', '3'], which would then result in a standaloneNumberError like this: '2 3'
    standaloneNumberError(' '.join(sourceMath))
    return sourceMath


def findBracketPairs(s, leftBracket="(", rightBracket=")"):
    bracketPairs = []

    leftBracketCount = 0
    rightBracketCount = 0

    for i in range(len(s)):
        if s[i] == leftBracket:
            bracketPairs.append([i, None])
            leftBracketCount += 1

        if s[i] == rightBracket:
            rightBracketCount += 1
            for pair in reversed(bracketPairs):
                if pair[1] == None:
                    pair[1] = i
                    break
    
    if leftBracketCount != rightBracketCount: # only triggers if unclosed brackets
        return None

    return bracketPairs
    

def isNumber(value): # returns True if it's a number, False otherwise
    try:
        float(value)
        return True
    except ValueError:
        return False


def standaloneNumberError(expression):
    isLastMeaningfulValueNumber = False # meaningful means non-whitespace
    isSpaceInbetween = False

    for character in expression:
        if isNumber(character):
            if isLastMeaningfulValueNumber and isSpaceInbetween:
                print(f"'{expression}'\n^ SyntaxError: Standalone number detected. Ensure your expression has operators.")
                exit(1)
            else:
                isLastMeaningfulValueNumber = True
                isSpaceInbetween = False
        elif character == " ":
            isSpaceInbetween = True
        else:
            isLastMeaningfulValueNumber = False
            isSpaceInbetween = False


if __name__ == "__main__":
    main()
    
