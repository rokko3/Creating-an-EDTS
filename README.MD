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
E -> T E' {E.traduccion= if E'.traduccion=="":
                T.traduccion
              else:
                E'.traduccion.unir(T.traduccion)}
E' -> opsuma T E' { E'.traduccion="suma("||T.traduccion||","||E1'.traduccion||")" }
E' -> opresta T E'{ E'.traduccion="resta("||T.traduccion||","||E1'.traduccion||")"}
E' -> ε {E'.traduccion=""}
T -> F T' { T.traduccion= if T'.traduccion == "":
                F.traduccion
              else:
                T'.traduccion.unir(F.traduccion) }
T' -> opmult F T' {T'.traduccion= "mul("||F.traduccion||","||T1'.traduccion||")"}
T' -> opdiv F T' { T'.traduccion="div("||F.traduccion||","||T1'.traduccion||")"}
T' -> ε {T'.traduccion=""}
F ->  parentesis_izq E parentesis_der {F.traduccion="("|| E.traduccion ||")"}
F -> entero { F.traduccion=entero.lexema}
F -> decimal F.traduccion=decimal.lexema
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