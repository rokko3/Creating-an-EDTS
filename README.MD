# Diseño de gramatica

```bash

E -> T E'
E' -> '+' T E' | '-' T E' | ε 
T -> F T'
T' -> '*' F T' | '/' F T' | ε
F -> '(' E ')' | num

```

## Gramatica de atributos

<table>
    <tr> 
        <td> Gramatica
<pre><code>
E -> T E'
E' -> '+' T E'
E' -> '-' T E'
E' -> ε
T -> F T'
T' -> '*' F T'
T' -> '/' F T' 
T' -> ε
F -> '(' E ')' 
F -> num
</code></pre>
    </td>
    <td> Accion Semantica
<pre><code>
E.traduccion= if E'.traduccion=="":
                T.traduccion
              else:
                E'.traduccion.unir(T.traduccion)
E'.traduccion="suma("||T.traduccion||","||E1'.traduccion||")"
E'.traduccion="resta("||T.traduccion||","||E1'.traduccion||")"
E'.traduccion=""
T.traduccion= if T'.traduccion == "":
                F.traduccion
              else:
                T'.traduccion.unir(F.traduccion)
T'.traduccion= "mul("||F.traduccion||","||T1'.traduccion||")"
T'.traduccion="div("||F.traduccion||","||T1'.traduccion||")"
T'.traduccion=""
F.traduccion="("|| E.traduccion ||")"
F.traduccion=num.lexema
</code></pre>
    </td>
  </tr>
</table>