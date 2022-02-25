import string
from typing import List

def main():
    sourceMath = "5 + 3_√(|8 - 1 - ( 5 * 2 ) * $frac[10][5]#|) * 2"
    print(solveSimpleExpression(sourceMath))


def solveSimpleExpression(sourceMath: string) -> int or float:
    """Precondition: 
        - sourceMath is formatted properly
        - sourceMath is not empty
    
    Return the solution to simple algebraic expressions as written 
    in sourceMath.

    'Simple' meaning without the use of math variables, such as x or y; just numbers and operators.

    help(convertToPythonMath) for more info on sourceMath.
    
    
    >>> solveSimpleExpression("4 * 99 - 5 // 9")
    43.44444444444444
    >>> solveSimpleExpression("2 + $frac[5][2]#")
    4.5
    """
    
    # exec function can't save values locally, so we're putting its values in a local dictionary to simulate a local scope
    execDict = {}

    pythonMath = convertToPythonMath(sourceMath)

    # exec function can execute strings as if it were actual code
    exec("execDict['result'] = " + pythonMath) 

    return execDict['result']
        

def convertToPythonMath(sourceMath: string) -> string:
    """Precondition:
        - sourceMath is formatted properly
        - sourceMath is not empty

    Return pythonMath- a python friendly version of sourceMath.

    sourceMath is, in essence, math formatted in a way a human would write. This is as opposed to math formatted in a way python would accept.

    
    Commands:
    Typically, in python, to denote a fraction of expressions, you would do the following:
        > (<<expression>>) / (<<expression>>)
    
    As a shorthand, use "//" instead:
        > <<expression>> // <<expression>>

    Can also use the built-in command:
        > "$frac[<<expression>>][<<expression2>>]#"
    Nested $frac[]# commands work. Can hold as many expressions/square brackets as desired. Expression cannot be empty.

    >>> convertToPythonMath("(3)(9)   ÷ 3")
    "(3)*(9)/3"
    >>> convertToPythonMath("(2 × 10 // 4) + 5")
    "(5)+5"
    """
    
    ## Alternative: 
    # return ''.join(changeCharacters(spaceOutOperators(sourceMath)))
    pythonMath = spaceOutEntities(sourceMath)
    pythonMath = convertEntities(pythonMath)
    return ''.join(pythonMath)
    

def convertEntities(sourceMath: List) -> List:
    """Precondition:
        - call through convertToPythonMath

    Take sourceMath - a list of entities (numbers, operators, brackets, commands, etc.) - and return it back after converting its values into
    python-friendly versions.

     >>> changeEntities(['2', '-', '$frac[3][1.5][2]#'])
    ['2', '-', '1']
    """

    # This code gives square bracket functionality. However, makes the code way slower. Pick your ~~tradeoff~~ poison.
    for i in range(len(sourceMath)):
        if sourceMath[i] == "[":
            sourceMath[i] = "("
        if sourceMath[i] == "]":
            sourceMath[i] = ")"

    # The incrementation is dynamic/non-linear, hence the non-pythonic loop
    i = 0
    while i != len(sourceMath):

        # Simply replaces human notation with python notation
        if sourceMath[i] == "^":
            sourceMath[i] = "**"
        if sourceMath[i] == "×":
            sourceMath[i] = "*"
        if sourceMath[i] == "÷":
            sourceMath[i] = "/"
        
        if sourceMath[i] == "|":
            sourceMath.insert(0, "(")
            sourceMath.append(")")

            # "| (|5-11|) -2|"
            #['(', '|', '(', '|', '5', '-', '11', '|', ')', '-', '2', '|', ')']
            
            bracketPairs = findBracketPairs(sourceMath, "|", "|")
            # [[1, 11], [3, 7]]

            for leftBracket, rightBracket in bracketPairs:
                sourceMath[leftBracket] = "(abs("
                sourceMath[rightBracket] = "))"
            
            del sourceMath[0]
            del sourceMath[-1]


        if sourceMath[i] == "√":
            root = 2

            # if we're rooting but isn't necessarily the default square root
            if sourceMath[i-1] == "_":
                if isNumber(sourceMath[i-2]):
                    root = convertToPythonMath(sourceMath[i-2])
                    del sourceMath[i-2 : i]
                    i -= 2
                

                elif sourceMath[i-2] == ")":
                    bracketPairs = findBracketPairs(sourceMath, "(", ")")

                    for leftBracket, rightBracket in bracketPairs:
                        if rightBracket == i-2:
                            startIndex = leftBracket + 1
                            endIndex = rightBracket

                    expression = convertToPythonMath(''.join(sourceMath[startIndex : endIndex]))

                    root = expression

                    # adjusting i with respect to how much we're about to delete
                    i -= len(sourceMath[startIndex-1 : endIndex+2])
                    del sourceMath[startIndex-1 : endIndex+2]               

                        


            # if it's just a number afterwards, root just that number
            if isNumber(sourceMath[i+1]):
                sourceMath[i] = "(pow({0}, 1/({1})))".format(sourceMath[i+1], root)
                del sourceMath[i+1]
            # root the whole expression inside of the brackets
            elif sourceMath[i+1] == "(":
                bracketPairs = findBracketPairs(sourceMath, "(", ")")

                for leftBracket, rightBracket in bracketPairs:
                    if leftBracket == i+1:
                        startIndex = leftBracket + 1
                        endIndex = rightBracket
                
                expression = convertToPythonMath(''.join(sourceMath[startIndex : endIndex]))

                sourceMath[i] = "(pow({0}, 1/({1})))".format(expression, root)
                del sourceMath[startIndex-1 : endIndex+1]

            
                
                    




        sourceMath, i = convertFractionCommands(sourceMath, i)

        # Handling traditional math conventions such as "3(2+2)" or "(5)(3-1)"
        if i != 0 and sourceMath[i][0] == "(" and (sourceMath[i - 1][-1] == ")" or isNumber(sourceMath[i - 1])):
                sourceMath.insert(i, "*")
                i += 1

        i += 1

    standaloneNumberError(' '.join(sourceMath))
    return sourceMath


def convertFractionCommands(sourceMath: List, i: int) -> List and int:
    """Precondition:
        - sourceMath is formatted properly

    Convert any fraction of expressions, then return sourceMath - a list of entities - along with the current index.
    """

    # Handling the shorthand for $frac; notation for a fraction of expressions
    if ''.join(sourceMath[i : i+2]) == "//":

        # Placing brackets at the very beginning and very end as a placeholder in case there aren't any actual brackets
        sourceMath.insert(0, "(")
        sourceMath.append(")")
        i += 1

        # Find the bracketPair that the fraction of expressions is immediately in. So, for "((3 + (3 * 1 // 2)) - (99))", it's able to discern for the brackets surrounding "3 * 1 // 2"
        bracketPairs = findBracketPairs(sourceMath, "(", ")")
        immediatePair = bracketPairs[0].copy()

        for leftBracket, rightBracket in bracketPairs:
            if leftBracket > immediatePair[0] and leftBracket < i and rightBracket > i:
                immediatePair[0], immediatePair[1] = leftBracket, rightBracket
        
        # Convert the fraction of expressions into a $frac command
        sourceMath[immediatePair[0] + 1] = "$frac[{0}][{1}]#".format(
            ''.join(sourceMath[immediatePair[0]+1 : i]), ''.join(sourceMath[i + 2 : immediatePair[1]])
        )
        
        # Once converted, delete everything we've already funnelled into the $frac command
        del sourceMath[immediatePair[0]+2 : immediatePair[1]]
        del sourceMath[0]
        del sourceMath[-1]
        i = immediatePair[0]

    
    # Convert a $frac command into it's actually number value
    if sourceMath[i][0:5] == "$frac":
        bracketPairs = findBracketPairs(sourceMath[i], "[", "]")
        # previousRightBracketIndex is necessary to properly handle nested $frac commands. Otherwise, it's unimportant.
        expressions = []
        previousRightBracketIndex = -1  # -1 is a placeholder

        # Evaluate expressions inside of each of $frac's squarebracket pairs
        for leftBracket, rightBracket in bracketPairs:
            if rightBracket > previousRightBracketIndex:
                previousRightBracketIndex = rightBracket
                expressions.append(convertToPythonMath(sourceMath[i][leftBracket + 1 : rightBracket]))

        total = ""
        for express in expressions:
            total += "(" + express + ")/"
        sourceMath[i] = "(" + total[:-1] + ")"
    
    return sourceMath, i
    

def spaceOutEntities(sourceMath: string) -> List:
    """Precondition:
        - call through convertToPythonMath

    Take raw sourceMath input, then split into a list of its entities: numbers, operators, brackets, commands, etc. Return it.

     >>> spaceOutEntities("2 + 3")
     ['2', '+', '3']
    """

    # A placeholder. Helps in avoiding indexErrors.
    sourceMath = list(sourceMath + " ") 


    i = 0
    while i != len(sourceMath):

        # Ensure there are spaces before and after each of these characters
        if sourceMath[i] in '÷×+-*/()[]^|√_':
            if sourceMath[i + 1] != " ":
                sourceMath.insert(i + 1, " ")
            if sourceMath[i - 1] != " ":
                sourceMath.insert(i, " ")
                i += 1
        
        # Turn $frac into one single entity in the list
        if ''.join(sourceMath[i : i+5]) == "$frac":
            bracketPairs = findBracketPairs(sourceMath, "$frac", "#")

            for pair in bracketPairs:
                if pair[0] == i:
                    endIndex = pair[1]

            # Set $frac up to become its own entity in the list
            fractionSubString = sourceMath[i:endIndex+1]
            fractionSubString = ''.join(fractionSubString)
            
            standaloneNumberError(fractionSubString)

            fractionSubString = fractionSubString.split() 
            fractionSubString = ''.join(fractionSubString)

            # Finally turning the $frac command into a single entity while deleting the leftovers
            sourceMath.insert(i, fractionSubString)
            del sourceMath[i+1 : endIndex+2]
        i += 1


    # joins everything into a single string, then splits them to remove whitespace
    sourceMath = ''.join(sourceMath)

    return sourceMath.split()


def findBracketPairs(s, leftBracket, rightBracket) -> List[List] or None:
    """Precondition:
        - None
        
    Returns index values for bracketPairs by comparing the specified leftBracket and rightBracket values onto the string in s.

    Will return None if brackets don't close properly.

    >>> findBracketPairs("blah blah blah blah", "b", "h")
    [[0, 3], [5, 8], [10, 13], [15, 18]]
    """

    bracketPairs = []
    sameBracket = ""

    # such as with opening and closing brackets for absolute values being the same character in |-5|, par exemple
    if leftBracket == rightBracket: 
        sameBracket = leftBracket  # (or rightBracket, cause they're the same)
        leftBracket = "("
        rightBracket = ")"
        

    leftBracketCount = 0
    rightBracketCount = 0

    for i in range(len(s)):
        if ''.join(s[i : i + len(leftBracket)]) == leftBracket:
            bracketPairs.append([i, None])
            leftBracketCount += 1

        if ''.join(s[i : i + len(rightBracket)]) == rightBracket:
            rightBracketCount += 1
            for pair in reversed(bracketPairs):
                if pair[1] == None:
                    pair[1] = i
                    break
    
    if leftBracketCount != rightBracketCount:
        return None

    # Making an assumption here. If this is math and they're the same bracket, regular brackets still exist and determine how these sameBrackets pair up
    if sameBracket:
        j = 0
        sameBracketIndexes = []
        
        for j in range(len(s)):
            if s[j] == sameBracket:
                immediatePair = bracketPairs[0].copy()

                for leftBracket, rightBracket in bracketPairs:
                    if leftBracket > immediatePair[0] and leftBracket < j and rightBracket > j:
                        immediatePair[0], immediatePair[1] = leftBracket, rightBracket

                sameBracketIndexes.append((j, immediatePair))

        sameBracketPairs = []
        k = 0
        while k < len(sameBracketIndexes):
            p = k + 1
            while p < len(sameBracketIndexes):
                if sameBracketIndexes[k][1] == sameBracketIndexes[p][1]:
                    sameBracketPairs.append(
                        [sameBracketIndexes[k][0], sameBracketIndexes[p][0]])
                    del sameBracketIndexes[p]
                    break
                p += 1
            k += 1
        return sameBracketPairs
    return bracketPairs
        

def isNumber(value: any) -> bool:
    """Precondition:
        - (None)

    Returns True if value is a number, False otherwise. 
    
    For the record, python has built-in functions meant to accomplish the same thing, but they aren't comprehensive enough.
    """

    try:
        float(value)
        return True
    except ValueError:
        return False


def standaloneNumberError(expression: string) -> None:
    """Precondition:
        - (None)

    Will raise an exception in a specific case of improper formatting.

    For example, "2 2" is not proper math notation. SyntaxError will be raised.
    """

    isLastMeaningfulValueNumber = False # meaningful means non-whitespace
    isSpaceInbetween = False

    for character in expression:
        if isNumber(character):
            if isLastMeaningfulValueNumber and isSpaceInbetween:
                raise SyntaxError("Standalone number detected. Ensure your expression has operators.")
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
    
