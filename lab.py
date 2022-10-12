from asyncio import SubprocessProtocol
import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Symbol:
    def __add__(self,y): # Binary operations symbol with symbolic expression reevaluates here
        return Add(self,y)
    def __radd__(self,y):
        return Add(y,self)
    def __sub__(self,y):
        return Sub(self,y)
    def __rsub__(self,y):
        return Sub(y,self)
    def __truediv__(self,y):
        return Div(self,y)
    def __rtruediv__(self,y):
        return Div(y,self)
    def __mul__(self,y):
        return Mul(self,y)
    def __rmul__(self,y):
        return Mul(y,self)
    def simplify(self): # Unless explicitly extended, simplifying has no change
        return self
    def __pow__(self,y):
        return Pow(self,y)
    def __rpow__(self,y):
        return Pow(y,self)


class Var(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n
        self.precedence=(4,4) # Highest precedence

    def __str__(self):
        ''' Returns name of variable'''
        return self.name

    def __repr__(self):
        return "Var(" + repr(self.name) + ")"
    
    def deriv(self,x):
        ''' Returns derivative with respect to x'''
        if(x == str(self)): # derivative of x with respect to x is 1
            return Num(1)
        else:
            return Num(0) # No correlation so deriv is 0
    def eval(self,mapping): 
        ''' Given dictionary with values to map to, returns value of variable '''
        # If str(self) not in mapping, return self
        return Num(mapping[str(self)])



class Num(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n
        self.precedence=(4,4)

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return "Num(" + repr(self.n) + ")"
    def deriv(self,x):
        return Num(0) # constant
    def eval(self,mapping):
        return self # Already defined
    

class BinOp(Symbol):

    def __init__(self,left,right) :
        '''Given left and right values of operation, sets self.right and self.left'''
        if(isinstance(left,str)):
            self.left = Var(left)
        elif((isinstance(left,int)) or isinstance(left,float)):
            self.left = Num(left)
        else:
            self.left = left
        if(isinstance(right,str)):
            self.right = Var(right)
        elif((isinstance(right,int)) or isinstance(right,float)):
            self.right = Num(right)
        else:
            self.right = right
    def __repr__(self):
        ''' Returns symbolic expression string of Binary operation'''
        return repr(self.left) + ", " + repr(self.right) # The internal part of repr, around which operation name will be added
    def __str__(self):
        ''' Returns string of operation using mathematical symbols'''
        p1 = self.precedence
        p2 = self.left.precedence
        p3 = self.right.precedence
        c1 = (p1[0]>p2[0]) or ((p1[0]==3) and (p2[0]==3)) # Conditions for left side to be parenthesized
        c2 = (p1[0]>p3[0]) or ((p1[0]==p3[0]) and (p1[1]==1)) # Conditions for right side to be parenthesized
        if(c1 and c2):
            return "(" + str(self.left)+") " + self.symbol+" (" + str(self.right) + ")"
        if(c1):
            return "(" + str(self.left)+") " + self.symbol + ' ' + str(self.right)
        if(c2):
            return str(self.left) + ' ' + self.symbol+" (" + str(self.right) + ")"
        return str(self.left) + ' ' + self.symbol + ' ' + str(self.right) # If no parentheses
    def eval(self,mapping):
        ''' Given binary operation and mapping, returns evaluated values of left and right to be preformed on'''
        return self.left.eval(mapping),self.right.eval(mapping) 
    def simplify(self):
        ''' Simplifies both left and right sides, and also checks if either are numbers that can then be simplified more'''
        k1 = self.left.simplify()
        k2 = self.right.simplify()
        c1=isinstance(k1,Num)
        c2 = isinstance(k2,Num)
        return (k1,k2,c1,c2)


class Add(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right) # Set left and right from BinOp
        self.symbol='+'
        self.precedence=(1,2)
    def __repr__(self):
        return "Add("+ super().__repr__() + ')'
    def deriv(self,x):
        return Add(self.left.deriv(x),self.right.deriv(x)) # Each derivative is independent of the other
    def simplify(self):
        k1,k2,c1,c2 = super().simplify()
        if(c1 and c2):
            return(Num(k1.n+k2.n))
        if(c1 and float(str(k1)) == 0 ):
            return k2
        if(c2 and float(str(k2)) == 0 ):
            return k1
        return Add(k1,k2)
    def eval(self,mapping):
        left,right = super().eval(mapping)
        return (Add(left,right).simplify()).n
        



    
    

class Sub(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.symbol='-'
        self.precedence=(1,1)
    def __repr__(self):
        return "Sub("+ super().__repr__() + ')'
    def deriv(self,x):
        return Sub(self.left.deriv(x),self.right.deriv(x)) # Each derivative is independent of the other
    def simplify(self):
        k1,k2,c1,c2 = super().simplify()
        if(c1 and c2):
            return(Num(k1.n-k2.n))
        if(c2 and float(str(k2)) == 0 ):
            return k1
        return Sub(k1,k2)
    def eval(self,mapping):
        left,right = super().eval(mapping)
        return (Sub(left,right).simplify()).n
    

class Mul(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.symbol='*'
        self.precedence=(2,2)
    def __repr__(self):
        return "Mul("+ super().__repr__() + ')'
    def deriv(self,x):
        return Add(Mul(self.left,self.right.deriv(x)),Mul(self.right,self.left.deriv(x))) # Apply product rule
    def simplify(self):
        k1,k2,c1,c2 = super().simplify()
        if(c1 and c2):
            return(Num(k1.n*k2.n))
        if(c1 and float(str(k1)) == 0 ):
            return Num(0)
        if(c2 and float(str(k2)) == 0 ):
            return Num(0)
        if(c1 and float(str(k1)) == 1 ):
            return k2
        if(c2 and float(str(k2)) == 1 ):
            return k1
        return Mul(k1,k2)
    def eval(self,mapping):
        left,right = super().eval(mapping)
        return (Mul(left,right).simplify()).n
    

class Div(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.symbol='/'
        self.precedence = (2,1)
    def __repr__(self):
        return "Div("+ super().__repr__() + ')'
    def deriv(self,x):
        return Div(Sub(Mul(self.right,self.left.deriv(x)),Mul(self.left,self.right.deriv(x))),Mul(self.right,self.right)) # Apply quotient rule
    def simplify(self):
        k1,k2,c1,c2 = super().simplify()
        if(c1 and c2):
            return(Num(k1.n/k2.n))
        if(c1 and float(str(k1)) == 0 ):
            return Num(0)
        if(c2 and float(str(k2)) == 1 ):
            return k1
        return Div(k1,k2)
    def eval(self,mapping):
        left,right = super().eval(mapping)
        return (Div(left,right).simplify()).n

class Pow(BinOp):
    def __init__(self,left,right):
        super().__init__(left,right)
        self.symbol='**'
        self.precedence = (3,3)
    def __repr__(self):
        return "Pow(" + super().__repr__()+")"
    def deriv(self,x):
        if(isinstance(self.right,Num)==False): # Cannot proceed if power is not a number
            print("The power should be a number")
            raise TypeError
        return Mul(Mul(self.right,Pow(self.left,Sub(self.right,Num(1)))),self.left.deriv(x)) # Apply chain rule of exponents
    def simplify(self):
        k1,k2,c1,c2 = super().simplify()
        if(c2 and float(str(k2)) == 0):
            return Num(1)
        if(c1 and c2):
            a=k1.n
            b=k2.n
            return Num(a**b)
        if(c2 and str(k2) == '0'):
            return Num(1)
        if(c2 and str(k2) == '1'):
            return k1
        if(c1 and str(k1) == '0'):
            return Num(0)
        return Pow(k1,k2)
    def eval(self,mapping):
        left,right = super().eval(mapping)
        return (Pow(left,right).simplify()).n

def findchar(string, char):
    '''Finds all indexes of char in string'''
    return [i for i, j in enumerate(string) if j == char] 

def tokenize(string):
    ''' Given parenthesized string of expression, creates array of tokens consisting either of parenthesis, number, of operation'''
    removespaces = string.split() # Split string into tokens by spaces
    finaltoken=[]
    for i in removespaces:
        left = len(findchar(i,'(')) # Find ( at beginning
        right = len(findchar(i,')')) # Find ) at end
        for j in range(left):
            finaltoken.append('(')
        finaltoken.append(i[left:len(i)-right]) # Number token between parentheses
        for j in range(right):
            finaltoken.append(')')
    return finaltoken

def parse(tokens):
    ''' Evaluates expressions given by tokens array'''
    def parse_expression(index):
        ''' Given index, returns value at index/starting at index as well as index of next expression'''
        if(tokens[index]=='('):
            leftexp,endleft = parse_expression(index+1) # Left expression
            expression = tokens[endleft] # Operation
            rightexp,rightend = parse_expression(endleft+1) # Right expression
            if(expression=='+'):
                return Add(leftexp,rightexp),(rightend+1)
            if(expression=='-'):
                return Sub(leftexp,rightexp),(rightend+1)
            if(expression=='*'):
                return Mul(leftexp,rightexp),(rightend+1)
            if(expression=='/'):
                return Div(leftexp,rightexp),(rightend+1)
            if(expression=='**'):
                return Pow(leftexp,rightexp),(rightend+1)
        elif(tokens[index][0]=='-' or tokens[index][0].isnumeric()):
            return Num(float(tokens[index])),index+1
        else:
            return Var(tokens[index]),index+1

    parsed_expression,next_index = parse_expression(0) # Returns expression starting at index 0 (so whole expression)
    return parsed_expression


def expression(string):
    ''' Given string of an expression, returns euivalent symbolic expression of string'''
    tokens=tokenize(string)
    evaluation = parse(tokens)
    return evaluation


    



if __name__ == "__main__":
    # doctest.testmod()
    result = Pow(Mul(Var('x'), Var('y')), Var('z'))
    result = result.eval({'z': 3, 'y': 89, 'x': 3})
    print(repr(result))


