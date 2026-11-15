# Tutorial de Squad-VoteTalkLimit

[English](./TUTORIAL.md) · [Türkçe](./TUTORIAL_TR.md) · **Español** · [简体中文](./TUTORIAL_ZH.md) · [Русский](./TUTORIAL_RU.md)

[README](./README_ES.md) · [Registro de cambios](./CHANGELOG.md)

Este tutorial va en orden desde un equipo vacío hasta una prueba de voz terminada. Ninguna variante se ha probado en un servidor real, así que la última parte explica cómo probar y qué informar.

---

## 📑 Contenido
1. [Descripción general](#-descripción-general)
2. [Paso a paso](#-paso-a-paso)
3. [Ajustes](#️-ajustes)
4. [Leer la prueba](#-leer-la-prueba)
5. [Solución de problemas](#-solución-de-problemas)
6. [Glosario](#-glosario)

---

## 🔭 Descripción general
### Qué hace

Mientras corren las votaciones de mapa y de facción de fin de partida, cada jugador tiene un presupuesto de habla. Hablar lo gasta, el silencio lo recarga. Cuando se vacía, el jugador queda silenciado un rato y luego puede hablar otra vez. Al terminar la votación todos quedan reactivados.

### Cómo funciona

Un ruleset de Blueprint (`BP_VoteTalkLimit`, padre `SQGameRuleSet`) corre en el servidor. En cada tick lee el estado de la votación, guarda un número por jugador (el presupuesto) y decide quién queda silenciado. Las dos variantes solo se diferencian en cómo llega el silencio a los jugadores:

- `server-only`: el servidor llama a `ToggleMutePlayer` en cada oyente.
- `client-rpc`: el servidor crea `BP_VTLClientHelper`, propiedad del controlador del que habla. Se replica solo a ese cliente. En ese cliente el auxiliar cambia la voz al empezar y la devuelve al terminar. El servidor fija su vida al tiempo de silencio y destruye todos los auxiliares al acabar la votación.

### Estructura de archivos

```
src/mod/server-only/VoteTalkLimit/   carpeta del mod de la variante server-only
src/mod/client-rpc/VoteTalkLimit/    carpeta del mod de la variante client-rpc
src/core/                            generadores de grafos (Python)
tests/integration/                   simulaciones de habla
docs/guides/                         notas
```

---

## 🪜 Paso a paso
**A. Consigue el Squad SDK.** Instala el Squad SDK (Unreal Editor) y abre el proyecto `SquadGame` una vez para que termine su primera carga.

**B. Elige una variante.** Descarga `VoteTalkLimit-server-only.zip` o `VoteTalkLimit-client-rpc.zip` de la [última versión](https://github.com/Miabeyefendi/Squad-VoteTalkLimit/releases/latest). Usa una a la vez.

**C. Copia el mod.** Descomprímelo en `Squad/Plugins/Mods/` dentro del SDK. El resultado es `Squad/Plugins/Mods/VoteTalkLimit/` con un archivo `VoteTalkLimit.mi` y una carpeta `Content`.

**D. Abre el proyecto.** Inicia el editor. Abre el Content Browser, activa la carpeta de contenido de plugins si hace falta y busca `VoteTalkLimit Content`.

**E. Abre el Blueprint.** Haz doble clic en `BP_VoteTalkLimit`. En la variante `client-rpc` mira también `BP_VTLClientHelper`.

**F. Compila.** Pulsa Compile. La línea de resultado debe decir "successful" sin avisos. Si no, consulta [Solución de problemas](#-solución-de-problemas).

**G. Guarda.** Guarda todos los assets.

**H. Empaqueta el mod.** Usa el comando de empaquetado de mods del SDK para el mod `VoteTalkLimit`. La documentación del SDK lo describe. El resultado es el mod cocinado que un servidor puede cargar.

**I. Sube a Workshop.** Sube el mod empaquetado al Steam Workshop como elemento privado o no listado para que solo lo use tu servidor de pruebas.

**J. Añádelo a ModLoader.** En el servidor, añade el mod a ModLoader como ruleset según describe la página de ModLoader. El propio mod ModLoader ya debe estar en el servidor.

**K. Ajustes opcionales.** Crea o edita `CustomOptions.cfg` en la carpeta de configuración del servidor. Consulta [Ajustes](#️-ajustes).

**L. Reinicia el servidor.** Arráncalo y comprueba en el registro que el mod se carga.

**M. Lado del cliente (solo `client-rpc`).** Los jugadores que entran descargan el mod de Workshop automáticamente si el servidor lo lista. Comprueba en el cliente de prueba que el mod está presente.

**N. Consigue un segundo jugador.** Hace falta uno que hable y otro que escuche en el mismo equipo o escuadra.

**O. Llega a una votación.** Juega o avanza una partida hasta el final para que se abra la votación de mapa.

**P. Habla.** El que habla dice una llamada corta una y otra vez sin pausa, por ejemplo "arriba al medio arriba al medio".

**Q. Escucha.** El oyente anota cuándo se corta la voz del que habla. El que habla anota los mensajes en pantalla.

**R. Espera a que acabe el silencio.** Tras el tiempo de silencio el que habla debería oírse otra vez.

**S. Comprueba el final de la votación.** Al terminar la votación el que habla debe quedar reactivado al instante, aunque no haya acabado el tiempo de silencio.

**T. Comprueba el marcador.** En el marcador antes de las votaciones nadie debe estar limitado.

**U. Comprueba una salida.** Silencia al que habla y haz que salga del servidor y vuelva a entrar. No debe seguir silenciado.

**V. Anota el resultado.** Consulta [Leer la prueba](#-leer-la-prueba).

**W. Prueba la otra variante.** Quita el mod, instala la otra variante y repite desde el paso C.

**X. Ajusta.** Cambia `VTL_TalkSeconds` y `VTL_MuteSeconds` a tu gusto.

**Y. Informa.** Abre un issue con la variante, lo que oíste y lo que viste en pantalla.

**Z. Quítalo.** Para desinstalar, quita el mod de ModLoader y borra la carpeta del mod.

---

## ⚙️ Ajustes
| Ajuste | Por defecto | Significado |
|---|---|---|
| `VTL_Enabled` | `true` | Interruptor general |
| `VTL_TalkSeconds` | `4.0` | Presupuesto de habla T |
| `VTL_MuteSeconds` | `10.0` | Duración del silencio M |

El presupuesto se recarga a `T / (T + M)` por segundo. Una frase larga se corta tras `T * (T + M) / M` segundos: 5,6 con los valores por defecto y 4,1 con `T = 3`, `M = 8`. Los ajustes se leen en vivo, así que un cambio se aplica sin recompilar.

### Dónde se guardan los ajustes

En el `CustomOptions.cfg` del servidor, leídos con las funciones de ajustes personalizados del SDK. La sintaxis exacta del archivo no se ha comprobado en un servidor real. Si un ajuste no parece aplicarse, se usa el valor por defecto del Blueprint.

---

## 🧪 Leer la prueba
Anota, para cada variante:

| Pregunta | Respuesta |
|---|---|
| ¿Se cortó al que habla tras unos T segundos hablando? | sí / no |
| ¿Dejó el oyente de oírlo? | sí / no |
| ¿Notó el que habla que lo silenciaban? | sí / no |
| ¿Se oyó otra vez al que habla tras M segundos? | sí / no |
| ¿Quedaron todos reactivados al terminar la votación? | sí / no |
| ¿Quedó alguien silenciado tras salir y volver a entrar? | sí / no |
| ¿Aparecieron los mensajes en pantalla? | sí / no |

---

## 🔧 Solución de problemas
### El Blueprint no compila

Abre el panel de resultados del compilador. Las causas habituales son que falte `BP_VTLClientHelper` (copia toda la carpeta `Content`) o una versión distinta del Squad SDK con pines renombrados.

### No se silencia nada

Es el resultado más probable de `server-only` si las funciones de silencio del SDK solo actúan en el cliente que las llama. Prueba `client-rpc`.

### Los mensajes aparecen pero la voz no se corta

La puerta y el presupuesto funcionan, solo falla el paso del silencio. Infórmalo con el nombre de la variante.

### Alguien se queda silenciado

Quita el mod de ModLoader y reinicia el servidor, luego infórmalo. Esto no debería ocurrir.

---

## ❓ Preguntas frecuentes
**¿Necesito SquadJS?** No. SquadJS no controla la voz.

**¿Afecta al marcador o a la partida?** No, solo a las votaciones de fin de partida.

---

## 📕 Glosario
- **Presupuesto**: los segundos de habla que le quedan a un jugador.
- **Puerta**: la condición "hay una votación en curso" que activa el límite.
- **Auxiliar**: `BP_VTLClientHelper`, el actor pequeño que usa la variante `client-rpc`.
- **Ruleset**: una clase Blueprint de ModLoader basada en `SQGameRuleSet`.
