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
        self.tokens = []
        self.pos = 0
        
    def parsear(self, tokens):
        self.tokens = tokens + [('$', '$')]
        self.pos = 0
        
        try:
            self.raiz = self._construir_arbol(self.simbolo_inicial)
            
            # Verificar que se consumieron todos los tokens
            if self.pos < len(self.tokens) - 1: 
                raise SyntaxError(f"Tokens adicionales no parseados: {self.tokens[self.pos:]}")
                
            return True, self.raiz
            
        except SyntaxError as e:
            return False, str(e)
    
    def _construir_arbol(self, simbolo):
        token_actual = self.tokens[self.pos][0] if self.pos < len(self.tokens) else '$'
        
        # Si es terminal
        if simbolo not in self.tabla:
            if simbolo == token_actual:
                # Crear nodo terminal
                valor_nodo = f"{simbolo}:{self.tokens[self.pos][1]}"
                nodo = Impresora.Nodo(valor_nodo)
                
                # ATRIBUTO SEMÁNTICO para terminales
                nodo.traduccion = self.tokens[self.pos][1]  # El lexema
                
                self.pos += 1
                return nodo
            else:
                raise SyntaxError(f"Error: se esperaba '{simbolo}', se encontró '{self.tokens[self.pos][1]}'")
        
        # Si es no terminal
        if token_actual in self.tabla[simbolo]:
            produccion = self.tabla[simbolo][token_actual]
            nodo = Impresora.Nodo(simbolo)
            
            if produccion != (self.epsilon,):
                hijos = []
                for s in produccion:
                    if s != self.epsilon:
                        hijo = self._construir_arbol(s)
                        hijos.append(hijo)
                        nodo.hijos.append(hijo)
                
                # ACCIONES SEMÁNTICAS según la producción
                self._aplicar_acciones_semanticas(nodo, simbolo, produccion, hijos)
            
            else:
                # Producción epsilon
                nodo.traduccion = ""
                
            return nodo
        else:
            esperados = list(self.tabla[simbolo].keys())
            raise SyntaxError(f"Error en {simbolo}: se esperaba {esperados}, se encontró '{token_actual}'")
    
    def _aplicar_acciones_semanticas(self, nodo, simbolo, produccion, hijos):

        if simbolo == "E":
            # E -> T E' 
            traduccion_t = hijos[0].traduccion
            traduccion_eprima = hijos[1].traduccion if len(hijos) > 1 else ""
            
            if traduccion_eprima == "":
                nodo.traduccion = traduccion_t
            else:
              
                nodo.traduccion = traduccion_eprima.replace("_", traduccion_t, 1)
        
        elif simbolo == "E'":
            if len(produccion) == 3 and produccion[0] == 'opsuma':
                # E' -> + T E'
                traduccion_t = hijos[1].traduccion
                traduccion_eprima1 = hijos[2].traduccion
                
                if traduccion_eprima1 == "":
                    # Solo hay una suma: suma(operando_izq, T)
                    nodo.traduccion = f"suma(_, {traduccion_t})"
                else:
                    # Hay más operaciones: suma(operando_izq, E')

                    parte_derecha = traduccion_eprima1.replace("_", traduccion_t, 1)
                    nodo.traduccion = f"suma(_, {parte_derecha})"
                
            elif len(produccion) == 3 and produccion[0] == 'opresta':
                # E' -> - T E'
                traduccion_t = hijos[1].traduccion
                traduccion_eprima1 = hijos[2].traduccion
                
                if traduccion_eprima1 == "":
                    # Solo hay una resta: resta(operando_izq, T)
                    nodo.traduccion = f"resta(_, {traduccion_t})"
                else:

                    parte_derecha = traduccion_eprima1.replace("_", traduccion_t, 1)
                    nodo.traduccion = f"resta(_, {parte_derecha})"
            else:
                # E' -> ε
                nodo.traduccion = ""
        
        elif simbolo == "T":
            # T -> F T' 
            traduccion_f = hijos[0].traduccion
            traduccion_tprima = hijos[1].traduccion if len(hijos) > 1 else ""
            
            if traduccion_tprima == "":
                nodo.traduccion = traduccion_f
            else:
                # T' ya trae la operación completa, reemplazamos el marcador
                nodo.traduccion = traduccion_tprima.replace("_", traduccion_f, 1)
        
        elif simbolo == "T'":
            if len(produccion) == 3 and produccion[0] == 'opmult':
                # T' -> * F T'
                traduccion_f = hijos[1].traduccion
                traduccion_tprima1 = hijos[2].traduccion
                
                if traduccion_tprima1 == "":
                    nodo.traduccion = f"mul(_, {traduccion_f})"
                else:
                    parte_derecha = traduccion_tprima1.replace("_", traduccion_f, 1)
                    nodo.traduccion = f"mul(_, {parte_derecha})"
                    
            elif len(produccion) == 3 and produccion[0] == 'opdiv':
                # T' -> / F T'
                traduccion_f = hijos[1].traduccion
                traduccion_tprima1 = hijos[2].traduccion
                
                if traduccion_tprima1 == "":
                    nodo.traduccion = f"div(_, {traduccion_f})"
                else:
                    parte_derecha = traduccion_tprima1.replace("_", traduccion_f, 1)
                    nodo.traduccion = f"div(_, {parte_derecha})"
            else:
                # T' -> ε
                nodo.traduccion = ""
        
        elif simbolo == "F":
            if produccion[0] == '(':
                # F -> ( E )
                nodo.traduccion = f"({hijos[1].traduccion})"
            else:
                # F -> entero | decimal
                nodo.traduccion = hijos[0].traduccion
        


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

def tabla_simbolos(tokens,lexemas):
    tabla = {}
    for tok, lex in zip(tokens, lexemas):
        tabla[lex] = tok
    print("--- TABLA DE SIMBOLOS ---")
    i = 0
    for lex in tabla:
        i+=1
        print(f"[{i}]. {lex}: {tabla[lex]}")
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

    print("\n--- ANALISIS SINTACTICO ---")
    exito, resultado = parser.parsear(tokens_lexicos)
    print(resultado)
    
    if exito:
        print("✓ Analisis sintactico EXITOSO")
        print("\n--- ARBOL DE ANALISIS ---")
        Impresora.imprimir_arbol(resultado)
        
        if hasattr(resultado, 'traduccion'):
            print(f"\n--- TRADUCCION ---")
            print(f"Resultado: {resultado.traduccion}")
    else:
        print("✗ Error sintáctico:", resultado)
        
    print("\n--- TOKENS LEXICOS ---")
    for tok, lexema in tokens_lexicos:
        print(f"{tok}: '{lexema}'")
    tabla_simbolos(*zip(*tokens_lexicos))
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
    
if __name__ == "__main__":
    main()
    
    