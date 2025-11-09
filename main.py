import sys
import Impresora
import analizador
reglas = {}
tokens={}
def reconocer_division(cadena, i):
    if cadena[i] == "/":
        return ["opdiv", "/", i+1]
    return None
def reconocer_entero(cadena, i):
    if i >= len(cadena) or not cadena[i].isdigit():
        return None
    
    inicio = i
    while i < len(cadena) and cadena[i].isdigit():
        i += 1
    if i < len(cadena) and cadena[i] == '.':
        return None 
    lexema = cadena[inicio:i]
    return ["entero", lexema, i]

def reconocer_decimal(cadena, i):

    if i >= len(cadena) or not cadena[i].isdigit():
        return None
    inicio = i
    # Parte entera
    while i < len(cadena) and cadena[i].isdigit():
        i += 1
    # Verificar punto decimal
    if i >= len(cadena) or cadena[i] != '.':
        return None  # No es decimal
    i += 1  # Consumir el punto
    
    if i >= len(cadena) or not cadena[i].isdigit():
        return None
    while i < len(cadena) and cadena[i].isdigit():
        i += 1
    
    lexema = cadena[inicio:i]
    return ["decimal", lexema, i]

def reconocer_opsuma(cadena, i):
    if cadena[i] == "+":
        return ["opsuma", "+", i+1]
    return None

def reconocer_opresta(cadena, i):
    if cadena[i] == "-":
        return ["opresta", "-", i+1]
    return None
def reconocer_multiplicacion(cadena, i):
    if cadena[i] == "*":
        return ["opmult", "*", i+1]
    return None
def reconocer_parentesis_izq(cadena, i):
    """Reconoce paréntesis izquierdo"""
    if cadena[i] == "(":
        return ["parentesis_izq", "(", i+1]
    return None

def reconocer_parentesis_der(cadena, i):
    """Reconoce paréntesis derecho"""
    if cadena[i] == ")":
        return ["parentesis_der", ")", i+1]
    return None

tokens = {
    'decimal': reconocer_decimal,     
    'entero': reconocer_entero,        
    'opsuma': reconocer_opsuma,
    'opresta': reconocer_opresta,
    'opmult': reconocer_multiplicacion,
    'opdiv': reconocer_division,
    'parentesis_izq': reconocer_parentesis_izq,
    'parentesis_der': reconocer_parentesis_der,
}
def lexer(cadena):
    """Analizador léxico principal"""
    i = 0
    lista_tokens = []
    while i < len(cadena):
        if cadena[i].isspace():  # ignorar espacios
            i += 1
            continue

        reconocido = None
        for nombre, funcion in tokens.items():
            resultado = funcion(cadena, i)
            if resultado:
                tok, lexema, j = resultado
                lista_tokens.append((tok, lexema))
                i = j
                reconocido = True
                break

        if not reconocido:
            raise ValueError(f"Error lexico: caracter inesperado '{cadena[i]}' en posicion {i}")

    return lista_tokens
class ParserPredictivo:
    def __init__(self, tabla_prediccion, simbolo_inicial):
        self.tabla = tabla_prediccion
        self.simbolo_inicial = simbolo_inicial
        self.epsilon = 'ε'
        
    def parsear(self, tokens):
        self.tokens = tokens + [('$', '$')]
        self.pos = 0
        self.pila = ['$', self.simbolo_inicial]
        self.nodos_pila = [Impresora.Nodo(self.simbolo_inicial)]
        self.raiz = self.nodos_pila[0]
        
        try:
            while self.pila:
                tope = self.pila[-1]
                token_actual = self.tokens[self.pos][0] if self.pos < len(self.tokens) else '$'
                
                print(f"DEBUG: Pila: {self.pila}, Token: {token_actual}")
                
                if tope == '$':
                    if token_actual == '$':
                        return True, self.raiz
                    else:
                        raise SyntaxError(f"Se esperaba fin de cadena")
                
                # Si el tope es un terminal
                if tope not in self.tabla:
                    if tope == token_actual:
                        self.pila.pop()
                        nodo_actual = self.nodos_pila.pop()
                        
                        nodo_hoja = Impresora.Nodo(f"{tope}:{self.tokens[self.pos][1]}")
                        nodo_actual.hijos.append(nodo_hoja)
                        
                        self.pos += 1
                    else:
                        raise SyntaxError(f"Error: se esperaba '{tope}', se encontró '{self.tokens[self.pos][1]}'")
                
                # Si el tope es un no terminal
                else:
                    if token_actual in self.tabla[tope]:
                        produccion = self.tabla[tope][token_actual]
                        self.pila.pop()
                        nodo_padre = self.nodos_pila.pop()
                        
                        print(f"DEBUG: Aplicando {tope} -> {produccion}")
                        
                        if produccion != (self.epsilon,):
                            # CORREGIDO: Crear los nodos hijos PRIMERO
                            hijos_nodos = []
                            for simbolo in produccion:
                                if simbolo != self.epsilon:
                                    nuevo_nodo = Impresora.Nodo(simbolo)
                                    hijos_nodos.append(nuevo_nodo)
                            
                            # CORREGIDO: Agregar hijos al padre ANTES de poner en pilas
                            nodo_padre.hijos.extend(hijos_nodos)
                            
                            # CORREGIDO: Poner en pilas en orden inverso, pero los NODOS en orden normal
                            for simbolo in reversed(produccion):
                                if simbolo != self.epsilon:
                                    self.pila.append(simbolo)
                            
                            # CORREGIDO: Poner los NODOS en la pila en el MISMO ORDEN que los símbolos
                            for simbolo in reversed(produccion):
                                if simbolo != self.epsilon:
                                    # Encontrar el nodo correspondiente
                                    for nodo in hijos_nodos:
                                        if nodo.valor == simbolo:
                                            self.nodos_pila.append(nodo)
                                            break
                        
                    else:
                        esperados = list(self.tabla[tope].keys())
                        raise SyntaxError(f"Error en {tope}: se esperaba {esperados}, se encontró '{token_actual}'")
            
            return True, self.raiz
            
        except SyntaxError as e:
            return False, str(e)
        
def construir_tabla_prediccion(prediccion):
    tabla = {}
    
    for (nt, prod), tokens in prediccion.items():
        if nt not in tabla:
            tabla[nt] = {}
        
        for token in tokens:

            token_limpio = token.strip("'")

            if isinstance(prod, list):
                prod_tuple = tuple(prod)
            else:
                prod_tuple = prod
                
            tabla[nt][token_limpio] = prod_tuple
    
    return tabla
def main():
    
    if len(sys.argv) != 3:
        print("Hace falta uno o mas archivos ")
        return
    

    nombre_archivo = sys.argv[1]
    cadena_prueba= sys.argv[2]

    gramatica,inicial=analizador.leer_gramatica(nombre_archivo)
    print(inicial)
    print("Gramática cargada de:", nombre_archivo)
    for nt in gramatica:
        print(nt, "->", [" ".join(p) for p in gramatica[nt]])
    
    primeros = analizador.calcular_primeros(gramatica)
    siguientes = analizador.calcular_siguientes(gramatica, inicial, primeros)
    pred=analizador.calcular_prediccion(gramatica, primeros, siguientes)
    
    tabla_prediccion = construir_tabla_prediccion(pred)
    parser = ParserPredictivo(tabla_prediccion, inicial)
    
    tokens_lexicos = lexer(cadena_prueba)
    
    print("\n--- ANÁLISIS SINTACTICO ---")
    exito, resultado = parser.parsear(tokens_lexicos)
    
    if exito:
        print("Analisis sintactico exitoso")

        Impresora.imprimir_arbol(resultado)
    else:
        print("Error sintactico:", resultado)
        
    print("\n--- TOKENS LEXICOS ---")
    for tok, lexema in tokens_lexicos:
        print(f"{tok}: '{lexema}'")
    """
    print("\n--- PRIMEROS ---")
    for nt in primeros:
        print(f"PRIMEROS({nt}) = {primeros[nt]}")

    print("\n--- SIGUIENTES ---")
    for nt in siguientes:
        print(f"SIGUIENTES({nt}) = {siguientes[nt]}")
        

    print("\n--- TABLA DE PARSING ---")
    for nt in tabla_prediccion:
        for token, produccion in tabla_prediccion[nt].items():
            print(f"M[{nt}, {token}] = {produccion}")
    """
if __name__ == "__main__":
    main()
    
    