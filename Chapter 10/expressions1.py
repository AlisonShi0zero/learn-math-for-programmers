from abc import ABC, abstractmethod
import math

def package(maybe_expression):
    if isinstance(maybe_expression, Expression):
        return maybe_expression
    elif isinstance(maybe_expression, int) or isinstance(maybe_expression, float):
        return Number(maybe_expression)
    else:
        raise ValueError("can't convert {} to expression.".format(maybe_expression))


class Expression(ABC):
    
    @abstractmethod
    def evaluate(self, **bindings):
        pass
    @abstractmethod
    def expand(self):
        pass

    @abstractmethod
    def display(self):
        pass

    @abstractmethod
    def derivative(self, var):
        pass

    @abstractmethod
    def substitude(self, var, exp):
        pass

    def __repr__(self):
        return self.display()

    def __add__(self, other):
        return Sum(self, package(other))
    
    def __sub__(self, other):
        return Difference(self, package(other))
    
    def __mul__(self, other):
        return Product(self, package(other))
    
    def __rmul__(self, other):
        return Product(package(other), self)
    
    def __truediv__ (self, other):
        return Quotient(self, package(other))
    
    def __pow__(self, other):
        return Power(self, package(other))
    
    @abstractmethod
    def _python_expr(self):
        pass
    
class Sum(Expression):
    def __init__(self, *exps):
        self.exps = exps

    def latex(self):
        return " + ".join(exp.latex() for exp in self.exps)
    
    def substitude(self, var, exp):
        return Sum(*[e.substitude(var, exp) for e in self.exps])
    
    def derivative(self, var):
        return Sum(*[exp.derivative(var) for exp in self.exps])

    def display(self):
        return f"Sum({','.join(e.display() for e in self.exps)})"

    def evaluate(self, **bindings):
        return sum([exp.evaluate(**bindings) for exp in self.exps])
    
    def expand(self):
        return Sum(*[exp.expand for exp in self.exps])
    
    def _python_expr(self):
        return " + ".join(f"({exp._python_expr()})" for exp in self.exps)
    

class Number(Expression):
    def __init__(self, number):
        self.number = number

    def latex(self):
        return str(self.number)
    
    def substitude(self, var, exp):
        return self
    
    def derivative(self, var):
        return Number(0)
    
    def display(self):
        return f"Number({self.number})"
    
    def evaluate(self, **bindings):
        return self.number
    
    def expand(self):
        return self
    
    def _python_expr(self):
        return str(self.number)
    
    
class Variable(Expression):
    def __init__(self, symbol):
        self.symbol = symbol

    def latex(self):
        return self.symbol
    
    def substitude(self, var, exp):
        if self.symbol == var.symbol:
            return exp
        else:
            return self
    
    def derivative(self, var):
        if self.symbol == var.symbol:
            return Number(1)
        else:
            return Number(0)

    def display(self):
        return f"Variable({self.symbol})"
    def evaluate(self, **bindings):
        try:
            return bindings[self.symbol]
        except:
            raise KeyError("Variable '{}' is not bound.".format(self.symbol))
        
    def expand(self):
        return self
    
    def _python_expr(self):
        return self.symbol
        
class Product(Expression):
    def __init__(self, exp1, exp2):
        self.exp1 = exp1
        self.exp2 = exp2

    def display(self):
        return f"Product({self.exp1.display()}, {self.exp2.display()})"
    
    def substitude(self, var, exp):
        return Product(self.exp1.substitude(var, exp), self.exp2.substitude(var, exp))

    def evaluate(self, **bindings):
        return self.exp1.evaluate(**bindings) * self.exp2.evaluate(**bindings)
    
    def expand(self):
        expanded1 = self.exp1.expand()
        expanded2 = self.exp2.expand()
        if isinstance(expanded1, Sum):
            return Sum(*[Product(e, expanded2).expand() for e in expanded1.exps])
        elif isinstance(expanded2, Sum):
            return Sum(*[Product(e, expanded1).expand() for e in expanded2.exps])
        else:
            return Product(expanded1, expanded2)
        
    def derivative(self, var):
        if not contains(self.exp1, var):
            return Product(self.exp1, self.exp2.derivative(var))
        elif not contains(self.exp2, var):
            return Product(self.exp1.derivative(var), self.exp2)
        else:
            return Sum(Product(self.exp1.derivative(var), self.exp2), 
                   Product(self.exp1, self.exp2.derivative(var)))
        
    def _python_expr(self):
        return f"({self.exp1._python_expr()})*({self.exp2._python_expr()})"
    

class Power(Expression):
    def __init__(self, base, exponent):
        self.base = base
        self.exponent = exponent

    def substitude(self, var, exp):
        return Power(self.base.substitude(var, exp), self.exponent.substitude(var, exp))

    def display(self):
        return f"Power({self.base.display()},{self.exponent.display()})"

    def evaluate(self, **bindings):
        return self.base.evaluate(**bindings) ** self.exponent.evaluate(**bindings)
    
    def expand(self):
        return self
    
    def derivative(self, var):
        if isinstance(self.exponent, Number):
            power_rule = Product(Variable(self.exponent.number), Power(self.base, Number(self.exponent.number-1)))
            return Product(self.base.derivative(var), power_rule)
        elif isinstance(self.base, Number):
            exponential_rule = Product(Apply(Function("ln"), Number(self.base.number)), self)
            return Product(self.exponent.derivative(var), exponential_rule)
        else:
            raise Exception(
                f"can't derivative of power {self.display()}"
            )
    
    def _python_expr(self):
        return f"({self.base._python_expr()})**({self.exponent._python_expr()})"
    

class Difference(Expression):
    def __init__(self, exp1, exp2):
        self.exp1 = exp1
        self.exp2 = exp2

    def display(self):
        return f"Difference({self.exp1.display()},{self.exp2.display()})"
    
    def substitude(self, var, exp):
        return Difference(self.exp1.substitude(var, exp), self.exp2.substitude(var, exp))

    def evaluate(self, **bindings):
        return self.exp1.evaluate(**bindings) - self.exp2.evaluate(**bindings)
    
    def expand(self):
        return self
    
    def derivative(self, var):
        return Difference(self.exp1.derivative(var), self.exp2.derivative(var))
    
    def _python_expr(self):
        return f"({self.exp1._python_expr()}) - ({self.exp2._python_expr()})"
    
class Quotient(Expression):
    def __init__(self, numerator, denumerator):
        self.numerator = numerator
        self.denumerator = denumerator

    def substitude(self, var, exp):
        return Quotient(self.numerator.substitude(var, exp), self.denumerator.substitude(var, exp))

    def display(self):
        return f"Quotient({self.numerator.display()},{self.denumerator.display()})"
    def evaluate(self, **bindings):
        return self.numerator.evaluate(**bindings) / self.numerator.evaluate(**bindings)
    
    def expand(self):
        return self
    
    def derivative(self, var):
        return Quotient(
            Difference(Product(self.numerator.derivative(var), self.denumerator), 
                       Product(self.numerator, self.denumerator.derivative(var))),
            Power(self.denumerator, Number(2))
        )
    def _python_expr(self):
        return f"({self.numerator._python_expr()}) / ({self.denumerator._python_expr()})"
    
class Negative(Expression):
    def __init__(self, exp):
        self.exp = exp

    def display(self):
        return f"Negative({self.exp.display()})"
    
    def substitude(self, var, exp):
        return Negative(self.exp.substitude(var, exp))
    
    def derivative(self, var):
        return Negative(self.exp.derivative(var))
    
    def evaluate(self, **bindings):
        return - self.exp.evaluate(**bindings)
    
    def expand(self):
        return self
    
    def _python_expr(self):
        return f"-({self.exp._python_expr()})"
    
class Function():
    def __init__(self, name):
        self.name = name

class Apply(Expression):
    def __init__(self, function, argumment):
        self.function = function
        self.argument = argumment

    def display(self):
        return f"Apply(Function(\"{self.function}\"), {self.argument.display()})"
    def evaluate(self, **bindings):
        return _function_bindings[self.function.name](self.argument.evaluate(**bindings))
    
    def expand(self):
        return Apply(self.function, self.argument.expand())
    
    def substitude(self, var, exp):
        return Apply(self.function, self.argument.substitude(var, exp))
    
    def derivative(self, var):
        return Product(self.argument.derivative(var), _derivative[self.function.name].substitude(_var, self.argument))
    
    def _python_expr(self):
        print(f"self.function:***{self.function}")
        return _function_python[self.function.name].format(self.argument._python_expr())



_function_bindings = {
    "sin": math.sin,
    "cos": math.cos,
    "ln": math.log,
    "sqrt": math.sqrt
}

_function_python = {
    "sin": "math.sin({})",
    "cos": "math.cos({})",
    "ln": "math.log({})",
    "sqrt": "math.sqrt({})"
}

_var = Variable("placeholder variable")

_derivative = {
    "sin": Apply(Function("cos"), _var),
    "cos": Product(Number(-1), Apply(Function("sin"), _var)),
    "ln": Quotient(Number(1), _var),
    "sqrt": Quotient(Number(1), Product(Number(2), Apply(Function("sqrt"), _var)))
}



def distinct_variables(exp):
    if isinstance(exp, Variable):
        return set(exp.symbol)
    elif isinstance(exp, Number):
        return set()
    elif isinstance(exp, Sum):
        return set().union(*[distinct_variables(exp) for exp in exp.exps])
    elif isinstance(exp, Product):
        return distinct_variables(exp.exp1).union(distinct_variables(exp.exp2))
    elif isinstance(exp, Power):
        return distinct_variables(exp.base).union(distinct_variables(exp.exponent))
    elif isinstance(exp, Apply):
        return distinct_variables(exp.argument)
    else:
        return TypeError("Not a valid Expression")
    

def contains(expression, variable):
    if isinstance(expression, Variable):
        return expression.symbol == variable.symbol
    elif isinstance(expression, Number):
        return False
    elif isinstance(expression, Sum):
        return any([contains(exp, variable) for exp in expression.exps])
    elif isinstance(expression, Product):
        return contains(expression.exp1, variable) or contains(expression.exp2, variable)
    elif isinstance(expression, Power):
        return contains(expression.base, variable) or contains(expression.exponent, variable)
    elif isinstance(expression, Quotient):
        return contains(expression.numerator, variable) or contains(expression.denumerator, variable)
    elif isinstance(expression, Apply):
        return contains(expression.argument, variable)
    elif isinstance(expression, Negative):
        return contains(expression.exp, variable)
    elif isinstance(expression, Difference):
        return contains(expression.exp1, variable) or contains(expression.exp2, variable)
    else:
        raise TypeError("Not a valid expression")
    

def dinstinct_functions(exp):
    if isinstance(exp, Number):
        return set()
    elif isinstance(exp, Variable):
        return set()
    elif isinstance(exp, Sum):
        return set().union(*[dinstinct_functions(exp) for exp in exp.exps])
    elif isinstance(exp, Product):
        return dinstinct_functions(exp.exp1).union(dinstinct_functions(exp.exp2))
    elif isinstance(exp, Power):
        return dinstinct_functions(exp.base).union(dinstinct_functions(exp.exponent))
    elif isinstance(exp, Apply):
        return set([exp.function.name]).union(dinstinct_functions(exp.argument))
    else:
        return TypeError("Not a valid Expression")
    

def contains_sum(exp):
    if isinstance(exp, Sum):
        return True
    elif isinstance(exp, Number):
        return False
    elif isinstance(exp, Variable):
        return False
    elif isinstance(exp, Product):
        return contains_sum(exp.exp1) or contains_sum(exp.exp2)
    elif isinstance(exp, Power):
        return contains_sum(exp.base) or contains_sum(exp.exponent)
    elif isinstance(exp, Difference):
        return contains_sum(exp.exp1) or contains_sum(exp.exp2)
    elif isinstance(exp, Quotient):
        return contains_sum(exp.numerator) or contains_sum(exp.denumerator)
    elif isinstance(exp, Negative):
        return contains_sum(exp.exp)
    elif isinstance(exp, Apply):
        return contains_sum(exp.argument)
    else:
        raise TypeError("Not a valid expression.")
    