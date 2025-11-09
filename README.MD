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
<pre><code> E -> T E'
E' -> '+' T E' | '-' T E' | ε
T -> F T'
T' -> '*' F T' | '/' F T' | ε
F -> '(' E ')' | num
</code></pre>
    </td>
    <td> Accion Semantica
<pre><code>
Gramaticah.t
h.as
a.asd
</code></pre>
    </td>
  </tr>
</table>